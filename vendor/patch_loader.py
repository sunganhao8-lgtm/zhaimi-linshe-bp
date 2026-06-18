"""
Patch the locally-downloaded vendor/amap/loader.js so that when it
injects the main AMap JS script tag, it uses the LOCAL maps.js
path (vendor/amap/maps.js) instead of the CDN URL.

The stock loader.js dynamically does:
    var l = document.createElement("script");
    l.src = "https://webapi.amap.com/maps?callback=___onAPILoaded&v="+d.AMap.version+"&key="+f+"&plugin="+d.AMap.plugins.join(",");

We rewrite that src to the local relative path. All other behavior
(callback handling, plugin detection, error handling) is untouched.
"""
import os
import re

LOADER = os.path.join(os.path.dirname(__file__), 'amap', 'loader.js')
ORIG = os.path.join(os.path.dirname(__file__), 'amap', 'loader.js.orig')
LOCAL_MAPS = 'vendor/amap/maps.js'  # path relative to site-map.html


def main() -> None:
    with open(LOADER, 'r', encoding='utf-8') as f:
        src = f.read()

    # Sanity check: this is the CDN URL we expect
    if 'https://webapi.amap.com/maps?' not in src:
        raise SystemExit('Could not find CDN maps URL in loader.js — loader may have changed format.')

    # Replace the single CDN URL with a relative local path
    patched = src.replace(
        'l.src="https://webapi.amap.com/maps?callback=___onAPILoaded',
        f'l.src="{LOCAL_MAPS}?callback=___onAPILoaded',
    )
    if patched == src:
        raise SystemExit('Patcher made no change — the exact string did not match.')

    # Strip out the v=, key=, and plugin= query parameters (the local maps.js
    # is already self-contained and version-locked, no need to re-include them).
    # Easier and safer to just leave the query alone — they are ignored by
    # the static maps.js response and don't cause errors.

    with open(LOADER, 'w', encoding='utf-8') as f:
        f.write(patched)

    # Also save an .orig copy the first time so the change is auditable
    if not os.path.exists(ORIG):
        with open(ORIG, 'w', encoding='utf-8') as f:
            f.write(src)
        print(f'Wrote original to {ORIG}')

    print(f'Patched {LOADER}')
    print(f'  before: ...l.src="https://webapi.amap.com/maps?callback=___onAPILoaded...')
    print(f'  after:  ...l.src="vendor/amap/maps.js?callback=___onAPILoaded...')


if __name__ == '__main__':
    main()
