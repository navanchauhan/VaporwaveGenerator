import re
import shutil
import wave
from random import randint

import numpy as np
from logzero import logger
from scipy import signal
from scipy.signal import find_peaks

CONFIDENCE_THRESH = 0.02


class VaporSong:
    def read_wav(src):
        with wave.open(src, "rb") as wav:
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            frames = wav.readframes(wav.getnframes())

        audio = VaporSong.decode_pcm(frames, sample_width)
        if channels > 1:
            audio = audio.reshape(-1, channels)
        return sample_rate, audio

    def decode_pcm(frames, sample_width):
        if sample_width == 1:
            return (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        if sample_width == 2:
            return np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
        if sample_width == 4:
            return np.frombuffer(frames, dtype="<i4").astype(np.float32) / 2147483648.0
        raise ValueError(f"Unsupported WAV sample width: {sample_width}")

    def write_wav(dest, sample_rate, audio):
        audio = np.asarray(audio, dtype=np.float32)
        audio = np.clip(audio, -1.0, 1.0)
        channels = 1 if audio.ndim == 1 else audio.shape[1]
        pcm = (audio * 32767.0).astype("<i2")
        with wave.open(dest, "wb") as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm.tobytes())

    def slow_down(src, rate, dest):
        if rate <= 0:
            raise ValueError("rate must be greater than zero")
        sample_rate, audio = VaporSong.read_wav(src)
        output_length = max(1, int(round(len(audio) / rate)))
        slowed = signal.resample(audio, output_length, axis=0)
        VaporSong.write_wav(dest, sample_rate, slowed)
        return dest

    def reverbize(src, dest):
        sample_rate, audio = VaporSong.read_wav(src)
        impulse_length = max(1, int(sample_rate * 0.35))
        impulse = np.zeros(impulse_length, dtype=np.float32)
        impulse[0] = 1.0
        delays = (0.045, 0.082, 0.131, 0.211, 0.337)
        gains = (0.45, 0.32, 0.24, 0.17, 0.11)
        for delay, gain in zip(delays, gains):
            index = min(impulse_length - 1, int(sample_rate * delay))
            impulse[index] += gain
        tail = np.exp(-np.linspace(0, 5, impulse_length, dtype=np.float32)) * 0.08
        impulse += tail

        if audio.ndim == 1:
            effected = signal.fftconvolve(audio, impulse, mode="full")[: len(audio)]
        else:
            effected = np.column_stack(
                [signal.fftconvolve(audio[:, channel], impulse, mode="full")[: len(audio)] for channel in range(audio.shape[1])]
            )

        fade_in = min(len(effected), int(sample_rate * 5))
        fade_out = min(len(effected), int(sample_rate * 7))
        if fade_in > 1:
            effected[:fade_in] *= np.linspace(0, 1, fade_in, dtype=np.float32).reshape((-1,) + (() if effected.ndim == 1 else (1,)))
        if fade_out > 1:
            effected[-fade_out:] *= np.linspace(1, 0, fade_out, dtype=np.float32).reshape((-1,) + (() if effected.ndim == 1 else (1,)))

        peak = float(np.max(np.abs(effected))) if effected.size else 0.0
        if peak > 1:
            effected /= peak
        VaporSong.write_wav(dest, sample_rate, effected)
        return dest

    def crop(src, dest, start, dur):
        sample_rate, audio = VaporSong.read_wav(src)
        start_frame = max(0, int(round(start * sample_rate)))
        end_frame = max(start_frame, int(round((start + dur) * sample_rate)))
        VaporSong.write_wav(dest, sample_rate, audio[start_frame:end_frame])

    def random_crop(src, max_sec_len, dest):
        sample_rate, audio = VaporSong.read_wav(src)
        f_len = int(len(audio) / sample_rate)
        if f_len <= max_sec_len:
            shutil.copyfile(src, dest)
            return
        start_region = f_len - max_sec_len
        start = randint(0, start_region)
        VaporSong.crop(src, dest, start, max_sec_len)

    def fetchbeats(src):
        """Return [time_seconds, confidence] beat records using Python audio analysis."""
        sample_rate, audio = VaporSong.read_wav(src)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        if audio.size == 0:
            return []

        frame_size = max(256, int(sample_rate * 0.046))
        hop_size = max(128, frame_size // 2)
        if audio.size < frame_size:
            return []

        frame_count = 1 + (audio.size - frame_size) // hop_size
        rms = np.empty(frame_count, dtype=np.float32)
        for index in range(frame_count):
            start = index * hop_size
            frame = audio[start : start + frame_size]
            rms[index] = np.sqrt(np.mean(frame * frame))

        onset = np.diff(rms, prepend=rms[0])
        onset[onset < 0] = 0
        max_onset = float(onset.max())
        if max_onset <= 0:
            return []

        onset /= max_onset
        min_distance = max(1, int(0.25 * sample_rate / hop_size))
        peaks, properties = find_peaks(
            onset,
            height=max(CONFIDENCE_THRESH, 0.1),
            distance=min_distance,
            prominence=0.05,
        )

        beats = []
        for peak, height in zip(peaks, properties["peak_heights"]):
            time_seconds = (peak * hop_size) / sample_rate
            beats.append([float(time_seconds), float(min(1.0, height))])
        return beats

    def split_beat(src, beat_matrix):
        split_files = []
        for i in range(0, len(beat_matrix) - 1):
            if beat_matrix[i][1] > CONFIDENCE_THRESH:
                dur = beat_matrix[i + 1][0] - beat_matrix[i][0]
                out = src.rsplit(".", 1)[0] + str(i) + ".wav"
                VaporSong.crop(src, out, beat_matrix[i][0], dur)
                split_files.append(out)
        return split_files

    def combine(sections, dest):
        output = []
        output_sample_rate = None
        for section in sections:
            for sample in section:
                sample_rate, audio = VaporSong.read_wav(sample)
                if output_sample_rate is None:
                    output_sample_rate = sample_rate
                elif sample_rate != output_sample_rate:
                    output_length = max(1, int(round(len(audio) * output_sample_rate / sample_rate)))
                    audio = signal.resample(audio, output_length, axis=0)
                output.append(audio)
        if not output or output_sample_rate is None:
            raise ValueError("No audio sections to combine.")
        combined = np.concatenate(output, axis=0)
        peak = float(np.max(np.abs(combined))) if combined.size else 0.0
        if peak > 1:
            combined /= peak
        VaporSong.write_wav(dest, output_sample_rate, combined)
        return dest

    def generate_sections(ary):
        sections = []
        beats = [4, 6, 8, 9]
        index = 0
        while index != len(ary):
            current_beat = beats[randint(0, len(beats) - 1)]
            new_section = []
            while current_beat != 0 and index != len(ary):
                new_section.append(ary[index])
                current_beat -= 1
                index += 1
            sections.append(new_section)
        return sections

    def dup_sections(sections):
        new_section = []
        for section in sections:
            new_section.append(section)
            if randint(0, 1) == 0:
                new_section.append(section)
        return new_section

    def make_passages(sections):
        passages = []
        index = 0
        while index != len(sections):
            passage_len = randint(1, 4)
            passage = []
            while index != len(sections) and passage_len > 0:
                passage.append(sections[index])
                index += 1
                passage_len -= 1
            passages.append(passage)
        return passages

    def reorder_passages(passages):
        new_passages = []
        passage_count = randint(5, 12)
        while passage_count != 0:
            passage = passages[randint(0, len(passages) - 1)]
            passage_count -= 1
            dup = randint(1, 4)
            while dup != 0:
                dup -= 1
                new_passages.append(passage)
        return new_passages

    def flatten(passages):
        sections = []
        for passage in passages:
            for section in passage:
                sections.append(section)
        return sections

    def vaporize_song(fname, title):
        logger.info("Slowing down the music")
        VaporSong.slow_down(fname, 0.7, "beats/out.wav")
        logger.info("Doing beat analysis")
        beat_matrix = VaporSong.fetchbeats("beats/out.wav")
        if len(beat_matrix) < 2:
            raise ValueError("Could not detect enough beats to vaporize the song.")
        logger.info("Split into beats")
        split_beats = VaporSong.split_beat("beats/out.wav", beat_matrix)
        if not split_beats:
            raise ValueError("Could not split the song into beat sections.")
        logger.info("Divide into sections")
        sections = VaporSong.generate_sections(split_beats)
        logger.info("Duping sections")
        duplicated = VaporSong.dup_sections(sections)
        passages = VaporSong.make_passages(duplicated)
        reordered = VaporSong.reorder_passages(passages)
        flattened = VaporSong.flatten(reordered)
        logger.info("Mastering & reverbing")
        VaporSong.combine(flattened, "beats/out_norev.wav")
        output_title = re.sub(r"\W+|_", " ", title).strip().replace(" ", "_") or "vaporwave"
        VaporSong.reverbize("beats/out_norev.wav", f"./{output_title}.wav")
        logger.info("Generated V A P O R W A V E")
