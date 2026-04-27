import wave
from pathlib import Path

import numpy as np

from src.VaporSong import VaporSong


def write_click_track(path: Path, sample_rate: int = 8000) -> None:
    duration_seconds = 3
    samples = np.zeros(sample_rate * duration_seconds, dtype=np.float32)
    for beat_second in (0.5, 1.0, 1.5, 2.0, 2.5):
        start = int(beat_second * sample_rate)
        samples[start : start + 80] = 0.9

    pcm = (samples * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())


def read_wav(path: Path):
    with wave.open(str(path), "rb") as wav:
        channels = wav.getnchannels()
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
    samples = np.frombuffer(frames, dtype="<i2").astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels)
    return sample_rate, samples


def test_fetchbeats_detects_click_track_without_external_binary(tmp_path):
    wav_path = tmp_path / "clicks.wav"
    write_click_track(wav_path)

    beats = VaporSong.fetchbeats(str(wav_path))

    assert len(beats) >= 4
    beat_times = [beat[0] for beat in beats]
    assert any(abs(beat_time - 0.5) < 0.08 for beat_time in beat_times)
    assert any(abs(beat_time - 1.0) < 0.08 for beat_time in beat_times)
    assert all(0 <= confidence <= 1 for _, confidence in beats)


def test_slow_down_writes_longer_wav(tmp_path):
    src = tmp_path / "clicks.wav"
    dest = tmp_path / "slow.wav"
    write_click_track(src)

    VaporSong.slow_down(str(src), 0.5, str(dest))

    _, original = read_wav(src)
    _, slowed = read_wav(dest)
    assert dest.exists()
    assert len(slowed) > len(original)


def test_crop_writes_requested_region(tmp_path):
    src = tmp_path / "clicks.wav"
    dest = tmp_path / "crop.wav"
    write_click_track(src)

    VaporSong.crop(str(src), str(dest), 0.5, 1.0)

    sample_rate, cropped = read_wav(dest)
    assert abs(len(cropped) - sample_rate) <= 1


def test_combine_concatenates_sections(tmp_path):
    first = tmp_path / "first.wav"
    second = tmp_path / "second.wav"
    dest = tmp_path / "combined.wav"
    write_click_track(first)
    write_click_track(second)

    VaporSong.combine([[str(first)], [str(second)]], str(dest))

    _, original = read_wav(first)
    _, combined = read_wav(dest)
    assert len(combined) == len(original) * 2


def test_reverbize_writes_wav(tmp_path):
    src = tmp_path / "clicks.wav"
    dest = tmp_path / "reverb.wav"
    write_click_track(src)

    VaporSong.reverbize(str(src), str(dest))

    assert dest.exists()
    _, reverbed = read_wav(dest)
    assert len(reverbed) > 0
