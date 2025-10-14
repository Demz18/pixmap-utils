#!/usr/bin/python3

import PIL.Image
import sys, os, io, math
import asyncio
import aiohttp
import json

USER_AGENT = "pmfun areaDownload 1.0 " + ' '.join(sys.argv[1:])
PPFUN_URL = "https://pixmap.fun"
CANVASES_URL = "https://raw.githubusercontent.com/Demz18/Pixmap-Area-Download/refs/heads/main/dist/canvases.json"

class Color(object):
    def __init__(self, index, rgb):
        self.rgb = rgb
        self.index = index

class EnumColorPixelplanet:
    ENUM = []

    def getColors(canvas):
        EnumColorPixelplanet.ENUM = []
        colors = canvas['colors']
        for i, color in enumerate(colors):
            if len(color) == 3:
                color = (*color, 255)
            EnumColorPixelplanet.ENUM.append(Color(i, tuple(color)))
    
    @staticmethod
    def index(i):
        for color in EnumColorPixelplanet.ENUM:
            if i == color.index:
                return color
        return EnumColorPixelplanet.ENUM[0]

class Matrix:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.width = None
        self.height = None
        self.matrix = {}

    def add_coords(self, x, y, w, h):
        if self.start_x is None or self.start_x > x:
            self.start_x = x
        if self.start_y is None or self.start_y > y:
            self.start_y = y
        end_x_a = x + w
        end_y_a = y + h
        if self.width is None or self.height is None:
            self.width = w
            self.height = h
        else:
            end_x_b = self.start_x + self.width
            end_y_b = self.start_y + self.height
            self.width = max(end_x_b, end_x_a) - self.start_x
            self.height = max(end_y_b, end_y_a) - self.start_y

    def create_image(self, filename=None):
        img = PIL.Image.new('RGBA', (self.width, self.height), (255, 0, 0, 0))
        pxls = img.load()
        for x in range(self.width):
            for y in range(self.height):
                try: 
                    color = self.matrix[x + self.start_x][y + self.start_y].rgb
                    pxls[x, y] = color
                except (IndexError, KeyError, AttributeError):
                    pass
        if filename is not None:
            if filename == 'b':
                b = io.BytesIO()
                img.save(b, "PNG")
                b.seek(0)
                return b
            else:
                img.save(filename)
        else:
            img.show()
        img.close()

    def set_pixel(self, x, y, color):
        if x >= self.start_x and x < (self.start_x + self.width) and y >= self.start_y and y < (self.start_y + self.height):
            if x not in self.matrix:
                self.matrix[x] = {}
            self.matrix[x][y] = color

async def fetch_canvases():
    headers = {'User-Agent': USER_AGENT}
    async with aiohttp.ClientSession() as session:
        async with session.get(CANVASES_URL, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Failed to fetch canvases.json: HTTP {resp.status}")
            text = await resp.text()
            data = json.loads(text)
            return data.get("canvases", data)

async def fetch(session, canvas_id, canvasoffset, ix, iy, target_matrix):
    url = f"{PPFUN_URL}/chunks/{canvas_id}/{ix}/{iy}.bmp"
    headers = {'User-Agent': USER_AGENT}
    max_attempts = 5

    for attempt in range(1, max_attempts + 1):
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.read()
                if len(data) != 65536:
                    print(f"[WARN] Chunk {ix},{iy} has invalid size ({len(data)}), attempt {attempt}/{max_attempts}")
                    await asyncio.sleep(1)
                    continue

                offset = int(-canvasoffset * canvasoffset / 2)
                off_x = ix * 256 + offset
                off_y = iy * 256 + offset

                for i, b in enumerate(data):
                    tx = off_x + i % 256
                    ty = off_y + i // 256
                    bcl = b & 0x7F
                    target_matrix.set_pixel(tx, ty, EnumColorPixelplanet.index(bcl))

                print(f"Loaded {url} with {len(data)} bytes")
                break

        except Exception as e:
            print(f"[ERROR] Error fetching {url} on attempt {attempt}: {e}")
            await asyncio.sleep(3)

        if attempt == max_attempts:
            print(f"[ERROR] Failed to load {url} after {max_attempts} attempts.")

async def get_area(canvas_id, canvas, x, y, w, h):
    target_matrix = Matrix()
    target_matrix.add_coords(x, y, w, h)
    canvasoffset = math.pow(canvas['size'], 0.5)
    offset = int(-canvasoffset * canvasoffset / 2)
    xc = (x - offset) // 256
    wc = (x + w - offset) // 256
    yc = (y - offset) // 256
    hc = (y + h - offset) // 256
    print(f"Loading from {xc} / {yc} to {wc + 1} / {hc + 1} PixelGetter")
    tasks = []
    async with aiohttp.ClientSession() as session:
        for iy in range(yc, hc + 1):
            for ix in range(xc, wc + 1):
                tasks.append(fetch(session, canvas_id, canvasoffset, ix, iy, target_matrix))
        await asyncio.gather(*tasks)
        return target_matrix

def validateCoorRange(ulcoor: str, brcoor: str, canvasSize: int):
    if not ulcoor or not brcoor:
        return "Not all coordinates defined"
    splitCoords = ulcoor.strip().split('_')
    if not len(splitCoords) == 2:
        return "Invalid Coordinate Format for top-left corner"
    
    x, y = map(lambda z: int(math.floor(float(z))), splitCoords)

    splitCoords = brcoor.strip().split('_')
    if not len(splitCoords) == 2:
        return "Invalid Coordinate Format for top-left corner"
    u, v = map(lambda z: int(math.floor(float(z))), splitCoords)
    
    if (u < x or v < y):
        return "Corner coordinates are aligned wrong"
    
    canvasMaxXY = canvasSize / 2
    canvasMinXY = -canvasMaxXY
    
    if (x < canvasMinXY or y < canvasMinXY or x >= canvasMaxXY or y >= canvasMaxXY):
        return "Coordinates of top-left corner are outside of canvas"
    if (u < canvasMinXY or v < canvasMinXY or u >= canvasMaxXY or v >= canvasMaxXY):
        return "Coordinates of bottom-right corner are outside of canvas"
    
    return (x, y, u, v)

async def main():
    canvases = await fetch_canvases()

    if len(sys.argv) != 5:
        print("Download an area of pixmap")
        print("Usage: areaDownload.py canvasID startX_startY endX_endY filename.png")
        print("Available canvases:")
        for canvas_id, canvas in canvases.items():
            if 'v' in canvas and canvas['v']:
                continue
            print(f"{canvas_id} = {canvas.get('title', '')}", end=', ')
        print()
        return

    canvas_id = sys.argv[1]

    if canvas_id not in canvases:
        print("Invalid canvas selected")
        return

    canvas = canvases[canvas_id]

    if 'v' in canvas and canvas['v']:
        print("Can't get area for 3D canvas")
        return

    parseCoords = validateCoorRange(sys.argv[2], sys.argv[3], canvas['size'])

    if (type(parseCoords) is str):
        print(parseCoords)
        sys.exit()
    else:
        x, y, w, h = parseCoords
        w = w - x + 1
        h = h - y + 1

    EnumColorPixelplanet.getColors(canvas)
    filename = sys.argv[4]

    matrix = await get_area(canvas_id, canvas, x, y, w, h)
    matrix.create_image(filename)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())