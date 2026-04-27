import shutil
import subprocess
from pathlib import Path

import cv2
from logzero import logger

from src.VHSImage import generateVHSStyle


def SaveVid(path, frame_dir="frames"):
    frame_path = Path(frame_dir)
    vid_obj = cv2.VideoCapture(path)
    count = 0
    while True:
        success, image = vid_obj.read()
        if not success:
            break
        cv2.imwrite(str(frame_path / f"{count}.jpg"), image)
        count += 1
    vid_obj.release()
    return count


def Style(path_to_frames, date=None, time="00:00"):
    frame_path = Path(path_to_frames)
    files = sorted(
        [path for path in frame_path.iterdir() if path.is_file()],
        key=lambda path: int(path.stem),
    )
    for count, frame in enumerate(files, start=1):
        out = frame.with_suffix(frame.suffix + ".styled.jpg")
        generateVHSStyle(str(frame), str(out), verbose=False, date=date, time=time)
        out.replace(frame)
        print("--------")
        print("On Frame: ")
        print(count)
        print("Out of")
        print(len(files))
        print("--------")


def generateVideo(outfile, path, infile):
    frame_path = Path(path)
    files = sorted(
        [path for path in frame_path.iterdir() if path.is_file()],
        key=lambda path: int(path.stem),
    )
    if not files:
        raise ValueError("No frames were extracted from the input video.")

    duration = subprocess.check_output(
        [
            "ffprobe",
            "-i",
            infile,
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ],
        text=True,
    )
    fps = len(files) / float(duration)
    print("FPS", fps)

    first = cv2.imread(str(files[0]))
    height, width, _ = first.shape
    size = (width, height)
    out = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    try:
        for frame in files:
            img = cv2.imread(str(frame))
            out.write(img)
    finally:
        out.release()


def VHS_Vid(infile, outfile, date=None, time="00:00"):
    path = Path("frames")
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir()
    try:
        logger.info("Extracting frames")
        SaveVid(infile, str(path))
        logger.info("Applying A E S T H E T I C S")
        Style(str(path), date=date, time=time)
        logger.info("Generating video")
        generateVideo("temp.mp4", str(path), infile)
        logger.info("Merging audio")
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                "temp.mp4",
                "-i",
                infile,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0?",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                outfile,
            ],
            check=True,
        )
    finally:
        logger.info("Removing residual files")
        Path("temp.mp4").unlink(missing_ok=True)
        Path("output-audio.aac").unlink(missing_ok=True)
