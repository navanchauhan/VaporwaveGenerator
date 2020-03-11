import requests
import datetime
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import colorsys
import json
import numpy as np
import imageio
import random
from math import floor
import os
import logzero
from logzero import logger
from logzero import setup_logger
import random


def generate_offsets(array_size, max_offset):
    periodicity = random.randint(1, 10)
    periodicity = random.random() * periodicity
    offsets = []
    for i in range(array_size):
        offsets.append(floor(max_offset*np.sin(periodicity*(i*np.pi/180))))
    return offsets


def hueChange(img, offset):
    # https://stackoverflow.com/questions/27041559/rgb-to-hsv-python-change-hue-continuously/27042106
    # It's better to raise an exception than silently return None if img is not
    # an Image.
    img.load()
    r, g, b = img.split()
    r_data = []
    g_data = []
    b_data = []

    offset = offset/100.
    for rd, gr, bl in zip(r.getdata(), g.getdata(), b.getdata()):
        h, s, v = colorsys.rgb_to_hsv(rd/255.0, bl/255.0, gr/255.0)
        rgb = colorsys.hsv_to_rgb(h, s+offset, v)
        rd, bl, gr = [int(x*255.) for x in rgb]
        r_data.append(rd)
        g_data.append(gr)
        b_data.append(bl)

    r.putdata(r_data)
    g.putdata(g_data)
    b.putdata(b_data)
    return Image.merge('RGB',(r,g,b))

def decision(probability):
    return random.random() < probability

def mod_image_repeat_rows(imgname, chance_of_row_repeat=0, max_row_repeats=0, min_row_repeats=0, save=True, out_name="image.jpg"):
    img = Image.open(imgname)
    pixels = img.load()
    width, height = img.size

    repeat = False
    num_repeats = 0
    times_to_repeat = 0
    row_to_repeat = []
    offsets = []
    for y in range(height):
        if not repeat and decision(chance_of_row_repeat):
            repeat = True
            times_to_repeat = random.randint(min_row_repeats, max_row_repeats)
            offsets = generate_offsets(times_to_repeat, random.randint(10, 50))
        for x in range(width):
            r, g, b = img.getpixel((x, y))

            if repeat and len(row_to_repeat) != width:
                pixels[x, y] = (r, g, b)
                row_to_repeat.append((r, g, b))
            elif repeat:
                try:
                    pixels[x, y] = row_to_repeat[x + offsets[num_repeats]]
                except Exception as e:
                    pixels[x, y] = row_to_repeat[x - offsets[num_repeats]]
            else:
                pixels[x, y] = (r, g, b)
        
        if repeat:
            num_repeats += 1
            if num_repeats >= times_to_repeat:
                repeat = False
                times_to_repeat = 0
                num_repeats = 0
                row_to_repeat = []
                offsets = []
    if save:
        img.save(out_name)


def add_date(img_path, out_name="image.jpg", bottom_offset=0):
    date_obj = datetime.datetime.now()
    date_str_1 = date_obj.strftime("%p %H:%M")
    date_str_2 = date_obj.strftime("%b. %d %Y")
    corner_offset = 50
    img = Image.open(img_path)
    width, height = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("src/VCR_OSD_MONO_1.001.ttf", 64)
    draw.text((corner_offset, (height-150-bottom_offset)), date_str_1, (255, 255, 255), font=font)
    draw.text((corner_offset, (height-75)-bottom_offset), date_str_2, (255, 255, 255), font=font)
    draw.text((corner_offset, 25), "|| PAUSE", (255, 255, 255), font=font)
    img.save(out_name)

def add_img_noise(imgpath, intensity=1, out_name="image.jpg"):
    img = imageio.imread(imgpath, pilmode='RGB')
    noise1 = img + intensity * img.std() * np.random.random(img.shape)
    imageio.imwrite(out_name, noise1)

def offset_hue(image, out_name="image.jpg"):
    if isinstance(image, str):
        image = Image.open(image)
        image = hueChange(image, 25)
        image.save(out_name)

def build_background(out_name, taskbar_offset):
    #getImage(out_name="start.jpg")
    offset_hue("start.jpg", out_name="saturated.jpg")
    mod_image_repeat_rows("saturated.jpg", 0.012, 50, 10, out_name="shifted.jpg")
    add_img_noise("shifted.jpg", out_name="noisy.jpg")
    add_date("noisy.jpg", out_name=out_name, bottom_offset=taskbar_offset)

"""
if __name__ == "__main__":
    build_background("bkg.jpg", 25)
"""    

def generateVHSStyle(infile, outfile, silence=False):
    if silence:
        cut_rows = bool(random.getrandbits(1))
        offset = random.choice([0,5,10])
        offset_hue(infile,"saturated.jpg")
        if cut_rows:
            mod_image_repeat_rows("saturated.jpg", 0.012, 50, 10, True, "shifted.jpg")
        else:
            mod_image_repeat_rows("saturated.jpg", 0, 0, 0, True, "shifted.jpg")
        add_date("shifted.jpg","noisy.jpg")
        add_date("noisy.jpg",outfile, bottom_offset=offset)
        os.remove("shifted.jpg")
        os.remove("saturated.jpg")
        os.remove("noisy.jpg")
    else:
        cut_rows = bool(random.getrandbits(1))
        offset = random.choice([0,5,10,15,20,25])
        logger.info("Saturating the image")
        offset_hue(infile,"saturated.jpg")
        if cut_rows:
            logger.info("Shifting the image")
            mod_image_repeat_rows("saturated.jpg", 0.012, 50, 10, True, "shifted.jpg")
        else:
            logger.info("Not applying lines effect")
            mod_image_repeat_rows("saturated.jpg", 0, 0, 0, True, "shifted.jpg")
        logger.info("Adding noise")
        add_date("shifted.jpg","noisy.jpg")
        logger.info("Adding text")
        add_date("noisy.jpg",outfile, bottom_offset=offset)
        logger.info("Generated Image: out.jpg")
        logger.info("Removing residual files")
        os.remove("shifted.jpg")
        os.remove("saturated.jpg")
        os.remove("noisy.jpg")

#generateVHSStyle("s.jpg","o.jpg")