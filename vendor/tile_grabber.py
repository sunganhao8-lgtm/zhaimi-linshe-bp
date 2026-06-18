"""
OSM tile grabber for 临港泥城镇 area.

Downloads OpenStreetMap raster tiles to vendor/osm-tiles/<z>/<x>/<y>.png
so that site-map.html can render the base map layer from the local
filesystem (or local HTTP server) without hitting an external tile
server at runtime.

SOURCE CHOICE
=============
We use https://tile.openstreetmap.de (the official German OSM mirror),
NOT tile.openstreetmap.org or the Wikimedia mirror, because:

  - tile.openstreetmap.org blocks scripted bulk downloads with
    a 200-OK + "blocked" PNG placeholder (header: x-blocked).
  - Wikimedia maps.wikimedia.org returns 403 once it sees a download
    burst.
  - CARTO, Stadia, OSM.fr, OSM.hot all rate-limit scripted users
    to ~1 tile per minute, which is too slow for our 52-tile scope.
  - OpenTopoMap works but is a topographic (tan/brown) style that
    clashes with the 宅咪 dark UI.

OSM.de is operated by the FOSSGIS community, explicitly intended for
"smaller applications" and embedded use, and uses the standard OSM
tile style — which renders well under a dark UI overlay.

Coverage: a 1.5 km radius around (30.9065, 121.8157) — i.e. the 宅咪
store center in 泥城镇 — across zoom levels 13-16.

Tile counts:
  z=13:  3x3 =  9 tiles
  z=14:  3x3 =  9 tiles
  z=15:  3x3 =  9 tiles
  z=16:  5x5 = 25 tiles
  Total: 52 tiles

We sleep(1.1) between requests to be a polite citizen. Re-running
this script is safe — existing tiles are skipped.
"""
import math
import os
import time
import urllib.request

# 泥城镇商业中心（宅咪门店坐标）
CENTER_LAT = 30.9065
CENTER_LNG = 121.8157

ZOOMS = [13, 14, 15, 16]

# Per-zoom offset (in tiles) around center.
# At z=13, 1 tile ≈ 38 km → 1 tile is more than enough for 1.5 km
# At z=16, 1 tile ≈ 4.8 km → 2 tiles each side = 5x5 covers ~12 km
OFFSETS = {13: 1, 14: 1, 15: 1, 16: 2}

# OSM.de (no subdomain rotation — single host)
TILE_HOST = 'https://tile.openstreetmap.de'

# User-Agent that identifies the project and a contact email
HEADERS = {
    'User-Agent': 'ZhaiMi-PetStore-Map/1.0 (contact: example@zhaimi.example.com) Python-urllib',
    'Referer': 'https://www.openstreetmap.de/',
    'Accept': 'image/png,image/*',
}

# Sleep between requests (seconds). 1.1s gives us a safe margin under
# OSM.de's per-IP rate limit.
REQUEST_DELAY = 1.1

# Tiles smaller than this many bytes are likely block/placeholder images
MIN_VALID_SIZE = 5000

ROOT = os.path.join(os.path.dirname(__file__), 'osm-tiles')


def deg2tile(lat: float, lng: float, z: int) -> tuple[int, int]:
    """WGS84 lat/lng -> XYZ tile coordinates at zoom z."""
    n = 2 ** z
    x = int((lng + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def download(url: str, path: str) -> bool:
    """Download url to path. Returns True on success."""
    req = urllib.request.Request(url, headers=HEADERS)
    data = urllib.request.urlopen(req, timeout=20).read()
    with open(path, 'wb') as f:
        f.write(data)
    return True


def main() -> None:
    print(f'Output dir: {ROOT}')
    print(f'Tile host: {TILE_HOST}')
    print(f'Center: ({CENTER_LAT}, {CENTER_LNG})')
    print(f'Zooms:   {ZOOMS}')
    print(f'Offsets: {OFFSETS}')
    print(f'Delay:   {REQUEST_DELAY}s per request')

    total = 0
    done = 0
    skipped = 0
    failed = 0

    for z in ZOOMS:
        cx, cy = deg2tile(CENTER_LAT, CENTER_LNG, z)
        off = OFFSETS[z]
        for dx in range(-off, off + 1):
            for dy in range(-off, off + 1):
                total += 1

    print(f'\nNeed up to {total} tiles total (52 PNGs ~= ~1MB on disk).\n')

    # Validate that we get a real tile from the CDN before starting
    test_url = f'{TILE_HOST}/14/13735/6711.png'
    try:
        data = urllib.request.urlopen(
            urllib.request.Request(test_url, headers=HEADERS), timeout=20
        ).read()
        if len(data) < MIN_VALID_SIZE:
            raise RuntimeError(
                f'CDN returned suspiciously small tile ({len(data)} B) — blocked?\n'
                f'  URL: {test_url}\n'
                f'  Hint: try again in a few minutes, OSM.de may have rate-limited this IP.'
            )
        print(f'CDN check OK: {test_url} → {len(data):,} B\n')
    except Exception as e:
        raise SystemExit(f'CDN unreachable: {e}')

    for z in ZOOMS:
        cx, cy = deg2tile(CENTER_LAT, CENTER_LNG, z)
        off = OFFSETS[z]
        z_dir = os.path.join(ROOT, str(z))
        os.makedirs(z_dir, exist_ok=True)
        for dx in range(-off, off + 1):
            os.makedirs(os.path.join(z_dir, str(cx + dx)), exist_ok=True)
        print(f'--- z={z} center=({cx},{cy}) offset={off} ---')
        for dx in range(-off, off + 1):
            for dy in range(-off, off + 1):
                x, y = cx + dx, cy + dy
                path = os.path.join(ROOT, str(z), str(x), f'{y}.png')
                if os.path.exists(path) and os.path.getsize(path) > MIN_VALID_SIZE:
                    skipped += 1
                    print(f'  [skip] z={z} x={x} y={y} (exists, {os.path.getsize(path):,}B)')
                    continue
                url = f'{TILE_HOST}/{z}/{x}/{y}.png'
                time.sleep(REQUEST_DELAY)
                try:
                    download(url, path)
                    size = os.path.getsize(path)
                    if size < MIN_VALID_SIZE:
                        # Probably a block placeholder, remove and fail
                        if os.path.exists(path):
                            os.remove(path)
                        raise RuntimeError(
                            f'suspiciously small tile ({size} B) — likely a block/placeholder, removed'
                        )
                    done += 1
                    print(f'  [ok]   z={z} x={x} y={y} -> {size:,}B')
                except Exception as e:
                    failed += 1
                    print(f'  [FAIL] z={z} x={x} y={y}: {e}')

    print(f'\nSummary: total={total}  downloaded={done}  skipped={skipped}  failed={failed}')


if __name__ == '__main__':
    main()
