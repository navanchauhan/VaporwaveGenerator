import argparse
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

from logzero import logger
from yt_dlp import YoutubeDL

from src.VHSImage import generateVHSStyle
from src.VHSVideo import VHS_Vid
from src.VaporSong import VaporSong

VERSION = "2.7.0"
MAX_DURATION = 600
YOUTUBE_URLS = (
    "youtube.com",
    "https://www.youtube.com/",
    "http://www.youtube.com/",
    "http://youtu.be/",
    "https://youtu.be/",
    "youtu.be",
)


def build_parser():
    parser = argparse.ArgumentParser(
        description="| V A P O R W A V E || G E N E R A T O R |",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-M", "--music", help="generate  v a p o r w a v e  music", action="store_true")
    mode.add_argument("-P", "--picture", help="generate VHS Style image", action="store_true")
    mode.add_argument("-V", "--video", help="VHS Style Video", action="store_true")
    parser.add_argument("-v", "--version", help="show program version", action="store_true")
    parser.add_argument("-i", "--input")
    parser.add_argument("-o", "--output", help="Output for specifying output video")
    parser.add_argument("-d", "--date", help="Custom Date in yyyy/mm/dd format. e.g 2020/5/14")
    parser.add_argument("-t", "--time", default="00:00", help="Custom Time in HH:MM format. e.g 11:23")
    return parser


def parse_args(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        args.mode = "version"
        return args

    if args.music:
        args.mode = "music"
    elif args.picture:
        args.mode = "picture"
    elif args.video:
        args.mode = "video"
    else:
        parser.error("one of --music, --picture, --video, or --version is required")

    if not args.input:
        parser.error("--input is required")
    if args.video and not args.output:
        parser.error("--output is required for video mode")

    return args


def ydl_options(request_id=1):
    return {
        "quiet": True,
        "format": "bestaudio/best",
        "outtmpl": f"{request_id}.%(ext)s",
        "prefer_ffmpeg": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }


def youtube_search(query):
    query_string = urllib.parse.urlencode({"search_query": query})
    with urllib.request.urlopen("https://www.youtube.com/results?" + query_string) as response:
        html = response.read().decode(errors="replace")
    seen = set()
    for video_id in re.findall(r"watch\?v=([A-Za-z0-9_-]{11})", html):
        if video_id not in seen:
            seen.add(video_id)
            yield "https://www.youtube.com/watch?v=" + video_id


def download_file(query, request_id=1):
    """Download a YouTube result or URL and extract it to a WAV file."""
    opts = ydl_options(request_id)
    original_path = f"{request_id}.wav"

    if query.lower().startswith(YOUTUBE_URLS):
        candidates = [query]
        logger.info("Query was a YouTube URL.")
    else:
        candidates = youtube_search(query)
        logger.info("Searching YouTube for: %s", query)

    selected_url = None
    selected_title = None
    with YoutubeDL(opts) as ydl:
        for url in candidates:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration") or 0
            if 5 <= duration <= MAX_DURATION:
                selected_url = url
                selected_title = info.get("title", "vaporwave")
                logger.info("Got video: %s", selected_title)
                break

        if not selected_url:
            raise ValueError("Could not find a video between 5 seconds and 10 minutes.")

        logger.info("Downloading video...")
        ydl.download([selected_url])

    return original_path, selected_title


def gen_vapor(file_path, title):
    shutil.rmtree("download", ignore_errors=True)
    shutil.rmtree("beats", ignore_errors=True)
    Path("download").mkdir()
    Path("beats").mkdir()
    try:
        VaporSong.vaporize_song(file_path, title)
    finally:
        shutil.rmtree("download", ignore_errors=True)
        shutil.rmtree("beats", ignore_errors=True)


def main(argv=None):
    args = parse_args(argv)
    if args.mode == "version":
        print("ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄", VERSION)
        return 0
    if args.mode == "music":
        name, title = download_file(args.input)
        gen_vapor(name, title)
        return 0
    if args.mode == "picture":
        generateVHSStyle(args.input, "out.jpg", date=args.date, time=args.time)
        return 0
    if args.mode == "video":
        VHS_Vid(args.input, args.output, date=args.date, time=args.time)
        return 0
    raise AssertionError(f"Unhandled mode: {args.mode}")


if __name__ == "__main__":
    raise SystemExit(main())
