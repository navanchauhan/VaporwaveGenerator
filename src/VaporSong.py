import os
import subprocess
import re
from random import randint

from sys import platform

import logzero
from logzero import logger
from logzero import setup_logger

CONFIDENCE_THRESH = 0.02

class VaporSong:

	# Slows down Track
	
	def slow_down(src, rate, dest):
		cmd = "sox -G -D " + src + " " + dest + " speed " + str(rate)
		os.system(cmd)
		return dest

	# Adds Reverb
	
	def reverbize(src, dest):
		cmd = "sox -G -D " + src + " " + dest + " reverb 100 fade 5 -0 7" # idk what this does tbh, https://stackoverflow.com/a/57767238/8386344
		os.system(cmd)
		return dest

	
	# Crops "src" from "start" plus "start + dur" and return it in "dest"
	def crop(src,dest,start,dur):
		cmd = "sox " + src + " " + dest + " trim " + " " + str(start) + " " + str(dur)
		os.system(cmd)

	
	# Randomly crops a part of the song of at most max_sec_len.
	def random_crop(src, max_sec_len, dest):
		out = subprocess.check_output(["soxi","-D",src]).rstrip()
		f_len = int(float(out))
		if (f_len <= max_sec_len):
			os.system("cp " + src + " " + dest)
			return
		else:
			start_region = f_len - max_sec_len
			start = randint(0,start_region)
			VaporSong.crop(src,dest,start,max_sec_len)

	
	# Given a file, returns a list of [beats, confidence], executable based on audibo's test-beattracking.c 
	# TODO: Move away from executable and use aubio's Python module
	def fetchbeats(src):
		beat_matrix = []
		if platform == 'darwin':
			beats = subprocess.check_output(["noah", "get-beats",src]).rstrip()
		else:
			beats = subprocess.check_output(["get-beats",src]).rstrip()
		beats_ary = beats.splitlines()
		for i in beats_ary:
			record = i.split()
			record[0] = float(record[0])/1000.0
			record[1] = float(record[1])
			beat_matrix.append(record)
		return beat_matrix

	# Splits an audio file into beats according to beat_matrix list
	
	def split_beat(src,beat_matrix):
		split_files = []
		for i in range(0,len(beat_matrix)-1):

			if(beat_matrix[i][1] > CONFIDENCE_THRESH):
				dur = (beat_matrix[i+1][0] - beat_matrix[i][0])
				out = src.split(".")[0]+str(i)+".wav"
				VaporSong.crop(src,out,beat_matrix[i][0],dur)
				split_files.append(out)
		return split_files

	# Combines a list of sections
	
	def combine(sections,dest):
		tocomb = []
		tocomb.append("sox")
		tocomb.append("-G")
		for section in sections:
			for sample in section:
				tocomb.append(sample)
		tocomb.append(dest)
		tmpFileLimit = len(tocomb) + 256 # in case the program messes up, it does not actually frick up your system
		n = str(tmpFileLimit)
		#logger.info("Setting file limit to ", n)
		os.system("ulimit -n " + n)
		subprocess.check_output(tocomb)
		return dest

	# Arbitrarily groups beats into lists of 4, 6, 8, or 9, perfect for looping.
	
	def generate_sections(ary):
		sections = []
		beats = [4,6,8,9]
		index = 0
		while(index != len(ary)):
			current_beat = beats[randint(0,len(beats)-1)]
			new_section = []
			while((current_beat != 0) and (index != len(ary))):
				new_section.append(ary[index])
				current_beat -= 1
				index += 1
			sections.append(new_section)
		return sections

	
	# given a list of sections, selects some of them and duplicates them, perfect for that vaporwave looping effect
	def dup_sections(sections):
		new_section = []
		for section in sections:
			new_section.append(section)
			if(randint(0,1) == 0):
				new_section.append(section)
		return new_section

	# a passage is a list of sections. This takes some sections and groups them into passages.
	
	def make_passages(sections):
		passages = []
		index = 0
		while(index != len(sections)):
			passage_len = randint(1,4)
			passage = []
			while(index != len(sections) and passage_len > 0):
				passage.append(sections[index])
				index += 1
				passage_len -= 1
			passages.append(passage)
		return passages

	# Given all of our passages, picks some of them and inserts them into a list some number of times.
	
	def reorder_passages(passages):
		new_passages = []
		passage_count = randint(5,12)
		while(passage_count != 0):
			passage = passages[randint(0,len(passages)-1)]
			passage_count -= 1
			dup = randint(1,4)
			while(dup != 0):
				dup -= 1
				new_passages.append(passage)
		return new_passages

	# converts a list of passages to a list of sections.
	
	def flatten(passages):
		sections = []
		for passage in passages:
			for section in passage:
				sections.append(section)
		return sections

	# It's all coming together
	
	def vaporize_song(fname, title):
		logger.info("Slowing down the music")
		VaporSong.slow_down(fname, 0.7, "beats/out.wav")
		#logger.info("Cropping")
		#VaporSong.random_crop("beats/out.wav",150,"beats/outcrop.wav")
		logger.info("Doing Beat Analysis")
		bm = VaporSong.fetchbeats("beats/out.wav")
		logger.info("Split into beats")
		splitd = VaporSong.split_beat("beats/out.wav",bm)
		#group beats to sections
		logger.info("Divide into sections")
		sections = VaporSong.generate_sections(splitd)
		logger.info("Duping Sections")
		sdup = VaporSong.dup_sections(sections)
		# group sections into passages
		paslist = VaporSong.make_passages(sdup)
		# reorder packages
		pasloop = VaporSong.reorder_passages(paslist)
		sectionflat = VaporSong.flatten(pasloop)
		logger.info("Mastering & Reverbing")
		VaporSong.combine(sectionflat,"beats/out_norev.wav")
		VaporSong.reverbize("beats/out_norev.wav","./" + (re.sub(r"\W+|_", " ", title)).replace(" ","_") + ".wav")
		logger.info("Generated V A P O R W A V E")
