# ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄
A ｖａｐｏｒｗａｖｅ music (+art, +video soon, I promise) generator bodged together using code from various sources. Runs on Python3

## Installation

This was tested on macOS Catalina ( so should work on almost all macOS versions).
Windows is unsupported at this time ( I need to find a way to use aubio's python module)

### Dependencies

#### Linux

```
sudo apt install ffmpeg libavl1 sox
pip install -r requirements.txt
```

#### macOS

Make sure you have brew installed

```
brew install noah # I would have had to re-compile the executeable :(
brew install sox
pip install -r requirements.txt

## Usage

### YouTube URL
```
python3 main.py <YOUTUBE_URL>
```
### Song Title
```
python3 main.py Song Title
```

## Bugs

This project is a result of bodging and therefore has tons of bugs which need to be ironed out

## To-Do

[ ] Move away from using os.system calls, and use Python modules instead ( Looking at you, Sox and aubio)
[ ] Clean the Code
[ ] Add Artwork Generator
[ ] Add Video Generator

## Credits

@WJLiddy His repo `Macintech` forms the base code for the music generator
@felipecustodio Using his repo `virtualdreamsbot` YouTube DL code ( Hopefully I will be able to integrate this project as a Telegram Bot)