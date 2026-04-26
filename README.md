[README.md](https://github.com/user-attachments/files/27104349/README.md)
# historyDownload.py

## Requirements

- **Python 3.8** or higher
  - `Pillow`
  - `aiohttp`

### FFmpeg (for timelapse generation)

FFmpeg is required only if you intend to compile the downloaded frames into a video. It is **not** required to run the downloader itself.

> 📺 **How to install FFmpeg:** [Watch the tutorial on YouTube](https://youtu.be/eRZRXpzZfM4?si=kbBCMU_5j_zYBMb3)

---

## Installation

**1. Clone or download this repository.**

```bash
git clone https://github.com/Demz18/Pixmap-Area-Download.git
cd Pixmap-Area-Download
```

**2. Install the required Python dependencies.**

```bash
pip install Pillow aiohttp
```

> On some systems you may need to use `pip3` instead of `pip`.

---

## Usage

```
python historyDownload.py <canvasID> <startX_startY> <endX_endY> <start_date> [end_date]
```

Running the script without arguments will display usage information and a list of available canvas IDs.

```bash
python historyDownload.py
```

Downloaded frames are saved sequentially in a `./timelapse/` folder that is created automatically.

---

## Arguments

| Argument | Description |
|---|---|
| `canvasID` | The identifier of the target canvas (e.g., `0`, `1`, `m`). Run the script with no arguments to see the full list. |
| `startX_startY` | Top-left corner of the area to capture, in `X_Y` format. Use the **R** key on the Pixmap.fun site to copy coordinates. |
| `endX_endY` | Bottom-right corner of the area to capture, in `X_Y` format. |
| `start_date` | The first date to capture, in `YYYY-MM-DD` format. |
| `end_date` *(optional)* | The last date to capture, in `YYYY-MM-DD` format. Defaults to today if omitted. |

---

## Examples

**Download a specific area across a date range:**

```bash
python historyDownload.py 0 -100_-100 100_100 2024-01-01 2024-03-31
```

---

## Generating a Timelapse with FFmpeg

Once all frames have been downloaded into the `./timelapse/` folder, use one of the following FFmpeg commands to compile them into a video.

**Standard output:**

```bash
ffmpeg -framerate 15 -f image2 -i timelapse/t%d.png -c:v libvpx-vp9 -pix_fmt yuva420p output.webm
```

**Lossless output:**

```bash
ffmpeg -framerate 15 -f image2 -i timelapse/t%d.png -c:v libvpx-vp9 -pix_fmt yuv444p -qmin 0 -qmax 0 -lossless 1 -an output.webm
```

**Scaled output (3× zoom) with an audio track:**

```bash
ffmpeg -i ./audio.mp3 -framerate 8 -f image2 -i timelapse/t%d.png \
  -map 0:a -map 1:v -vf scale=iw*3:-1 -shortest \
  -c:v libvpx-vp9 -c:a libvorbis -pix_fmt yuva420p output.webm
```

---

## Notes

- **Frame skipping:** To reduce the number of output frames and speed up processing, you can increase the `frameskip` variable at the top of the script. A value of `1` captures every frame; `2` captures every other frame; and so on.
- **Faulty backups:** If the full daily backup for a given date is missing or corrupt (i.e., returns a solid-color image), the script will automatically substitute the last valid frame from the previous day.
- **Coordinate reference:** Use the **R** key while viewing the canvas on [pixmap.fun](https://pixmap.fun) to copy the coordinates of any point to your clipboard.
- **3D canvases:** Canvases marked as three-dimensional (`v: true`) are not supported and will be skipped.
