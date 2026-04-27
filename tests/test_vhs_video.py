from pathlib import Path

import src.VHSVideo as vhs_video


def test_vhs_vid_interpolates_audio_merge_commands(monkeypatch, tmp_path):
    commands = []
    frames = tmp_path / "frames"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vhs_video, "SaveVid", lambda infile, path="frames": None)
    monkeypatch.setattr(vhs_video, "Style", lambda path, date=None, time="00:00": None)
    monkeypatch.setattr(vhs_video, "generateVideo", lambda outfile, path, infile: Path(outfile).write_bytes(b"video"))
    monkeypatch.setattr(vhs_video.subprocess, "run", lambda cmd, check: commands.append(cmd))

    vhs_video.VHS_Vid("input video.mp4", "out video.mp4")

    assert frames.exists()
    assert [
        "ffmpeg",
        "-y",
        "-i",
        "temp.mp4",
        "-i",
        "input video.mp4",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0?",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        "out video.mp4",
    ] in commands
