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

def webp_dimensions(path):
    with path.open('rb') as f:
        header = f.read(12)
        if header[:4] != b'RIFF' or header[8:12] != b'WEBP':
            raise ValueError(f'Invalid WebP: {path.name}')
        while chunk := f.read(8):
            kind, length = chunk[:4], struct.unpack('<I', chunk[4:])[0]
            if kind == b'VP8X':
                data = f.read(10)
                return 1 + int.from_bytes(data[4:7], 'little'), 1 + int.from_bytes(data[7:10], 'little')
            if kind == b'VP8 ':
                data = f.read(10)
                return struct.unpack('<H', data[6:8])[0] & 0x3fff, struct.unpack('<H', data[8:10])[0] & 0x3fff
            if kind == b'VP8L':
                data = f.read(5)
                bits = int.from_bytes(data[1:], 'little')
                return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
            f.seek(length + length % 2, 1)
    raise ValueError(f'Missing WebP dimensions: {path.name}')

photos = []
state_path = ROOT / 'scripts/webp-progress.json'
state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
originals = {path.name: path for path in (ROOT / 'assets/gallery').glob('*.jpg')}
webps = {path.stem + '.jpg': path for path in (ROOT / 'assets/gallery-webp').glob('*.webp') if not path.name.endswith('.tmp.webp')}
for name in sorted(originals.keys() | webps.keys()):
    path = originals.get(name)
    webp = webps.get(name)
    width, height = dimensions(path) if path else webp_dimensions(webp)
    photo = {'file': name, 'width': width, 'height': height}
    entry = state.get(name, {})
    if webp and (not path or (entry.get('mtime_ns') == path.stat().st_mtime_ns
            and entry.get('source_bytes') == path.stat().st_size and entry.get('webp_bytes') == webp.stat().st_size)):
        width, height = webp_dimensions(webp)
        photo.update(webp=webp.name, width=width, height=height)
    photos.append(photo)
(ROOT / 'assets/photos.json').write_text(json.dumps(photos, separators=(',', ':')), encoding='utf-8')
print(f'Catalog: {len(photos)} photos')
