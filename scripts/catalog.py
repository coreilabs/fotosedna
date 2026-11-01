"""Rebuild the gallery catalog using Python only; original images are untouched."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def dimensions(path):
    with path.open('rb') as f:
        if f.read(2) != b'\xff\xd8':
            raise ValueError(f'Invalid JPEG: {path.name}')
        while True:
            byte = f.read(1)
            if not byte:
                raise ValueError(f'Missing JPEG dimensions: {path.name}')
            if byte != b'\xff':
                continue
            marker = f.read(1)
            while marker == b'\xff':
                marker = f.read(1)
            if marker in (b'\x00', b'\xd8'):
                continue
            length = struct.unpack('>H', f.read(2))[0]
            if marker[0] in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                _, height, width = struct.unpack('>BHH', f.read(5))
                return width, height
            f.seek(length - 2, 1)

photos = []
for path in sorted((ROOT / 'assets/gallery').glob('*.jpg')):
    width, height = dimensions(path)
    photos.append({'file': path.name, 'width': width, 'height': height})
(ROOT / 'assets/photos.json').write_text(json.dumps(photos, separators=(',', ':')), encoding='utf-8')
print(f'Catalog: {len(photos)} photos')
