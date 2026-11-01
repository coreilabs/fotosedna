"""Decode all converted images before optionally deleting corresponding JPGs."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--delete-originals', action='store_true')
    args = parser.parse_args()
    if (ROOT / 'scripts/webp-conversion.lock').exists():
        parser.error('Wait until the conversion finishes before verification/deletion.')
    magick = shutil.which('magick')
    if not magick:
        parser.error('ImageMagick is required.')
    original_root = (ROOT / 'assets/gallery').resolve()
    output_root = (ROOT / 'assets/gallery-webp').resolve()
    state = json.loads((ROOT / 'scripts/webp-progress.json').read_text(encoding='utf-8'))
    originals = sorted(original_root.glob('*.jpg'))
    outputs = []
    for original in originals:
        output = (output_root / (original.stem + '.webp')).resolve()
        entry = state.get(original.name, {})
        if (original.resolve().parent != original_root or output.parent != output_root
                or not output.is_file() or entry.get('mtime_ns') != original.stat().st_mtime_ns
                or entry.get('source_bytes') != original.stat().st_size
                or entry.get('webp_bytes') != output.stat().st_size):
            parser.error(f'Missing or outdated conversion: {original.name}. No originals deleted.')
        outputs.append(output)
    print(f'Verifying {len(outputs)} WebP files. Originals remain until ALL checks pass.', flush=True)
    def verify(batch):
        subprocess.run([magick, '-regard-warnings', *map(str, batch), 'null:'],
                       check=True, capture_output=True, timeout=180)
        return len(batch)
    verified = 0
    with ThreadPoolExecutor(max_workers=2) as pool:
        batches = [outputs[i:i+32] for i in range(0, len(outputs), 32)]
        for count in pool.map(verify, batches):
            verified += count
            if verified % 320 == 0 or verified == len(outputs):
                print(f'Verified {verified}/{len(outputs)}', flush=True)
    if args.delete_originals:
        # Exact files only, after validating resolved roots and every converted image.
        for original in originals:
            original.unlink()
        print(f'Deleted {len(originals)} verified JPG originals.', flush=True)
        subprocess.run([sys.executable, str(ROOT / 'scripts/catalog.py')], check=True)
        subprocess.run([sys.executable, str(ROOT / 'scripts/version_assets.py'), '--force'], check=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
