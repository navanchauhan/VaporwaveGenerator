import os
import cv2
from src.VHSImage import generateVHSStyle
from os.path import isfile, join
import subprocess
from logzero import logger


def SaveVid(path):
    vidObj = cv2.VideoCapture(path)
    count = 0
    success = 1
    while success:
        success, image = vidObj.read()
        cv2.imwrite("frames/" + str(count) + ".jpg", image)
        # os.rename("frames/"+str(count)+".jpg", os.path.splitext("frames/"+str(count)+".jpg")[0])
        count += 1


def Style(pathToFrames,date=None,time="00:00"):
    files = [f for f in os.listdir(pathToFrames) if isfile(join(pathToFrames, f))]
    count = 0
    for i in files:
        count += 1
        f = str(i)
        fi = pathToFrames + f
        out = fi + ".jpg"

        generateVHSStyle(fi, out, verbose=False,date=date,time=time)
        os.rename(out, fi)
        print("--------")
        print("On Frame: ")
        print(count)
        print("Out of")
        print(len(files))
        print("--------")
    cwd = os.getcwd()
    os.chdir(pathToFrames)
    c = "find ./ -name \"*.jpg\" -exec sh -c 'mv $0 `basename \"$0\" .jpg`' '{}' \;    ;"
    os.system(c)
    os.chdir(cwd)


def generateVideo(outfile, path, infile):
    frame_array = []
    files = [int(f) for f in os.listdir(path) if isfile(join(path, f))]
    files.sort()

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
            "csv=%s" % ("p=0"),
        ]
    )
    fps = len(files) / float(duration)
    print("FPS", fps)

    for i in range(len(files)):
        filename = path + str(files[i])
        img = cv2.imread(filename)
        height, width, _ = img.shape
        size = (width, height)
        frame_array.append(img)
    out = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*"MP4V"), fps, size)
    for i in range(len(frame_array)):
        out.write(frame_array[i])
    out.release()


def VHS_Vid(infile, outfile,date=None,time="00:00"):
    path = "./frames/"
    os.system("rm frames/*")
    os.system("mkdir frames")
    logger.info("Exctracting Frames")
    try:
        SaveVid(infile)
    except:
        logger.debug("Extracted Frames")
    logger.info("Applying A E S T H E T I C S")
    Style(path,date=date,time=time)
    logger.info("Generating Vidio")
    generateVideo("temp.mp4", path, infile)
    logger.info("Extracting audio of original video")
    os.system("ffmpeg -i %(infile)s -vn -acodec copy output-audio.aac")
    logger.info("Merging audio")
    os.system("ffmpeg -i temp.mp4 -i output-audio.aac -c copy %(outfile)s")
    logger.info("Removing residual files")
    os.remove("temp.mp4")
    os.remove("output-audio.aac")


# VHS_Vid("video.mp4","video2.mp4")
