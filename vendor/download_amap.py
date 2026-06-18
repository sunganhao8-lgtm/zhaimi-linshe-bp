"""
Download AMap JS API files to local vendor/ directory.

This makes site-map.html load the AMap loader.js and main maps JS
from local files instead of the CDN, so the page no longer depends
on webapi.amap.com for its JS resources.

POI/Walking REST API calls are NOT affected - those still go to
restapi.amap.com via fetch() as before.
"""
import urllib.request
import os
import ssl

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'amap')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Use a browser-like User-Agent to avoid CDN rejections
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'http://localhost/',
    'Accept': '*/*',
}

# (URL, output_filename)
URLS = [
    (
        'https://webapi.amap.com/loader.js',
        'loader.js',
    ),
    (
        'https://webapi.amap.com/maps?v=2.0'
        '&key=47ff8f012ae1c05def4454f0285bbbc9'
        '&plugin=AMap.PlaceSearch,AMap.Walking,AMap.Driving,AMap.Geocoder',
        'maps.js',
    ),
]


def download(url: str, out_path: str) -> int:
    """Download url to out_path. Returns bytes downloaded."""
    print(f'  -> GET {url}')
    req = urllib.request.Request(url, headers=HEADERS)
    # Default SSL context works on most systems; fall back to unverified on errors
    try:
        ctx = ssl.create_default_context()
        data = urllib.request.urlopen(req, timeout=60, context=ctx).read()
    except ssl.SSLError:
        print('  ! SSL error, retrying without verification')
        ctx = ssl.create_unverified_context()
        data = urllib.request.urlopen(req, timeout=60, context=ctx).read()
    with open(out_path, 'wb') as f:
        f.write(data)
    return len(data)


def main() -> None:
    print(f'Output dir: {OUTPUT_DIR}')
    for url, name in URLS:
        out = os.path.join(OUTPUT_DIR, name)
        print(f'\n[{name}]')
        size = download(url, out)
        print(f'  -> wrote {out} ({size:,} bytes)')
    print('\nDone.')


if __name__ == '__main__':
    main()
