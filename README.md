# ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄

A ｖａｐｏｒｗａｖｅ music + image + video (+art soon, I promise) generator bodged together using code from various sources. Runs on Python 3. VHSVideo option is really really slow (Seconds per frame is 7.)

```
ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄 2.5
usage: main.py [-h] [-M] [-P] [-V] [-v] [-i INPUT] [-o OUTPUT] [-d DATE]
               [-t TIME]

| V A P O R W A V E || G E N E R A T O R |

optional arguments:
  -h, --help            show this help message and exit
  -M, --music           generate v a p o r w a v e music
  -P, --picture         generate VHS Style image
  -V, --video           VHS Style Video
  -v, --version         show program version
  -i INPUT, --input INPUT
  -o OUTPUT, --output OUTPUT
                        Output for specifying output video
  -d DATE, --date DATE  Custom Date in yyyy/mm/dd format. e.g 2020/5/14
  -t TIME, --time TIME  Custom Time in HH:MM format. e.g 11:23                   
```

If the program gives an error for sox, try running `ulimit -n 999'`. You may also need to run `chmod +x get-beats`

## Demo

### M U S I C

Sample Album:

https://www.bandlab.com/programming_psychic/albums/844f21a0-fa65-ea11-a94c-0003ffd19c0f

### V H S  I M A G E

#### Input

![](assets/in-vhs.jpg?raw=true "Input VHS")

#### Output

![](assets/out-vhs.jpg?raw=true "Output VHS")

### V H S  V I D E O

See `in.mp4` and `out.mp4` in the `assets` folder

#### Input

![](assets/in.gif?raw=true "Input Video")

#### Output

![](assets/out.gif?raw=true "Output Video")


## Installation

This was tested on macOS Catalina ( so should work on almost all macOS versions).
Windows is unsupported at this time ( I need to find a way to use aubio's python module)

### Dependencies

#### Linux

```
sudo apt install ffmpeg ffprobe libavl1 sox
pip install -r requirements.txt
```

#### macOS

Make sure you have brew installed

```
brew install noah # I would have had to re-compile the executeable :(
brew install sox
pip install -r requirements.txt
```

## Usage

### M U S I C

#### YouTube URL
```
python3 main.py -M -i <YOUTUBE_URL>
```
#### Song Title
```
python3 main.py -M -i Song Title
```

### V H S  I M A G E S

`python3 main.py -P -i "image.jpg"`

### V H S  V I D E O

`python3 main.py -V -i "video.mp4" -o "output.mp4"`

## Bugs

This project is a result of bodging and therefore has tons of bugs which need to be ironed out. I need to swat some bugs in the VHSVideo file.

There might be a problem with the generated video not having audio, for that run the following 

`ffmpeg -i video.mp4 -vn -acodec copy output-audio.aac`
`ffmpeg -i output.mp4 -i output-audio.aac -c copy output-with-audio.mp4`


## To-Do

- [ ] Move away from using os.system calls, and use Python modules instead ( Looking at you, Sox and aubio)
- [x] Clean the Code
- [ ] Add Artwork Generator
- [x] VHS Picture Styler ( Added in v1.5 )
- [x] Add Video Generator
- [x] Add Custom Date to VHS Styler

## Credits

@WJLiddy His repo `Macintech` forms the base code for the music generator

@felipecustodio Using his repo `virtualdreamsbot` YouTube DL code ( Hopefully I will be able to integrate this project as a Telegram Bot)

@Ragex04 His repo `VHS_BingImages` forms the base code for the VHS Image Styler
