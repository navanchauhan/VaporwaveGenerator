# ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄

A ｖａｐｏｒｗａｖｅ music + image + video (+art soon, I promise) generator bodged together using code from various sources. Runs on Python 3. VHSVideo option is really really slow.

```
ｖａｐｏｒｗａｖｅ　ｇｅｎｅｒａｔｏｒ　旺育栄 2.7
usage: vaporwave-generator [-h] [-M | -P | -V] [-v] [-i INPUT] [-o OUTPUT]
                           [-d DATE] [-t TIME]

| V A P O R W A V E || G E N E R A T O R |

options:
  -h, --help            show this help message and exit
  -M, --music           generate  v a p o r w a v e  music
  -P, --picture         generate VHS Style image
  -V, --video           VHS Style Video
  -v, --version         show program version
  -i INPUT, --input INPUT
  -o OUTPUT, --output OUTPUT
                        Output for specifying output video
  -d DATE, --date DATE  Custom Date in yyyy/mm/dd format. e.g 2020/5/14
  -t TIME, --time TIME  Custom Time in HH:MM format. e.g 11:23
```

Music mode downloads audio with `yt-dlp`, then uses Python audio processing to slow it down, detect beats, rearrange beat sections, and add reverb. Image mode adds saturation, VHS row glitches, noise, timestamp text, and a pause overlay. Video mode extracts frames with OpenCV, applies the image effect to each frame, rebuilds the video, and merges the original audio back with `ffmpeg`.

## Installation

Install system tools:

### Linux

```bash
sudo apt install ffmpeg
```

### macOS

```bash
brew install ffmpeg uv
```

Install Python dependencies:

```bash
uv sync
```

The old `get-beats` Linux binary, aubio, noah, and Sox are no longer required. Music transformations now run through the Python code in `src/VaporSong.py`.

## Usage

```bash
uv run vaporwave-generator --help
```

### M U S I C

```bash
uv run vaporwave-generator -M -i "<YOUTUBE_URL>"
uv run vaporwave-generator -M -i "Song Title"
```

### V H S  I M A G E S

```bash
uv run vaporwave-generator -P -i "image.jpg"
uv run vaporwave-generator -P -i "image.jpg" -d 2020/5/14 -t 11:23
```

The image output is written to `out.jpg`.

### V H S  V I D E O

```bash
uv run vaporwave-generator -V -i "video.mp4" -o "output.mp4"
```

Video styling is slow because it applies the full image pipeline to every extracted frame.

## Development

Run tests with:

```bash
uv run --extra dev pytest
```

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

See `in.mp4` and `out.mp4` in the `assets` folder.

#### Input

![](assets/in.gif?raw=true "Input Video")

#### Output

![](assets/out.gif?raw=true "Output Video")

## To-Do

- [x] Replace `get-beats` binary with Python beat detection
- [x] Replace Sox music transforms with Python audio processing
- [x] Move Python dependency management to `uv`
- [x] Clean up CLI argument handling
- [x] Add VHS picture styler
- [x] Add video generator
- [x] Add custom date to VHS styler
- [ ] Add artwork generator

## Credits

@WJLiddy His repo `Macintech` forms the base code for the music generator.

@felipecustodio Using his repo `virtualdreamsbot` YouTube downloader code.

@Ragex04 His repo `VHS_BingImages` forms the base code for the VHS image styler.
