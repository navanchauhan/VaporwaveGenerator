from src.VaporSong import VaporSong
from src.VHSImage import generateVHSStyle
from src.VHSVideo import VHS_Vid
import os
import sys
import youtube_dl
import logzero
from logzero import logger
from logzero import setup_logger
import re
import urllib.request
import urllib.parse
import argparse
import time

version = 2.0
style = False

text = '| V A P O R W A V E || G E N E R A T O R |'

parser = argparse.ArgumentParser(description = text)
parser.add_argument("-M", "--music", help="generate  v a p o r w a v e  music", action="store_true")
parser.add_argument("-P", "--picture", help="generate VHS Style image", action="store_true")
parser.add_argument("-V","--video", help="VHS Style Video", action="store_true")
parser.add_argument("-v", "--version", help="show program version", action="store_true")
parser.add_argument("-i", "--input")
parser.add_argument("-o","--output", help="Output for specifying output video")


args = parser.parse_args()

music = False
picture = False
video = False

if args.version:
	print("ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄", version)
	exit
if args.music:
	music = True
elif args.picture:
    picture = True
elif args.video:
    video = True
if args.input:
	query = args.input
if args.output:
    outfile = args.output
else:
    parser.print_help()
    exit

MAX_DURATION = 600 # In-case the program finds a compilation
youtube_urls = ('youtube.com', 'https://www.youtube.com/', 'http://www.youtube.com/', 'http://youtu.be/', 'https://youtu.be/', 'youtu.be')

def download_file(query,request_id=1):
    """Returns audio to the vapor command handler

    Searches YouTube for 'query', finds first match that has
    duration under the limit, download video with youtube_dl
    and extract .wav audio with ffmpeg.

    Query can be YouTube link. 
    """
    ydl_opts = {
        'quiet': 'True',
        'format': 'bestaudio/best',
        'outtmpl': str(request_id) +'.%(ext)s',
        'prefer_ffmpeg': 'True', 
        'noplaylist': 'True',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    original_path = str(request_id) + ".wav"
    file_title = ""

    # check if query is youtube url
    if not query.lower().startswith((youtube_urls)):
        # search for youtube videos matching query
        query_string = urllib.parse.urlencode({"search_query" : query})
        html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
        info = False

        # find video that fits max duration
        logger.info("Get video information...")
        for url in search_results:
            # check for video duration
            try:
                info = youtube_dl.YoutubeDL(ydl_opts).extract_info(url,download = False)
            except Exception as e:
                logger.error(e)
                raise ValueError('Could not get information about video.')
            full_title = info['title']
            if (info['duration'] < MAX_DURATION and info['duration'] >= 5):
                # get first video that fits the limit duration
                logger.info("Got video: " + str(full_title))
                file_title = info['title']
                break
        
        # if we ran out of urls, return error
        if (not info):
            raise ValueError('Could not find a video.')

    # query was a youtube link
    else:
        logger.info("Query was a YouTube URL.")
        url = query
        info = youtube_dl.YoutubeDL(ydl_opts).extract_info(url,download = False)
        file_title = info['title']
        # check if video fits limit duration
        if (info['duration'] < 5 or info['duration'] > MAX_DURATION):
            raise ValueError('Video is too short. Need 5 seconds or more.')

    # download video and extract audio
    logger.info("Downloading video...")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            logger.error(e)
            raise ValueError('Could not download ' + str(full_title) + '.')

    return original_path, file_title


def gen_vapor(filePath, title):
	# Delete stuff if there is anything left over.
	os.system("rm -r download/")
	os.system("rm -r beats/")

    # Make the proper folders for intermediate steps
	os.system("mkdir download/")
	os.system("mkdir beats/")


	# Download the youtube query's first result. Might be wrong but YOLO
	#YTDownloader.download_wav_to_samp2(query)

	# For every song in download folder(just one for now)
	"""
	for fs in os.listdir("download/"):
		# Slow down the song.
		VaporSong.vaporize_song(query,"download/"+fs)
		pass
	# When we are finished, delete the old folders.
	"""
	VaporSong.vaporize_song(filePath, title)

	os.system("rm -r download/")
	os.system("rm -r beats/")


"""	
## Makes this a command line tool: disable when we get the webserver going
sys.argv.pop(0)
query = ""
for s in sys.argv:
	query = query + s
"""

if music:
    name, title = download_file(query)
    gen_vapor(name, title)
elif picture:
    generateVHSStyle(query,"out.jpg")
elif video:
    VHS_Vid(query, outfile)
    