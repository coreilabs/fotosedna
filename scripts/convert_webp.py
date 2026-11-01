"""Resumable, batched WebP conversion. Requires Python and ImageMagick (magick)."""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'assets/gallery-webp'
STATE = ROOT / 'scripts/webp-progress.json'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch-size', type=int, default=100)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--quality', type=int, default=82)
    parser.add_argument('--all', action='store_true', help='Process all remaining batches; otherwise process one batch.')
    parser.add_argument('--delete-originals', action='store_true', help='After conversion, verify ALL outputs and delete matching JPG originals.')
    args = parser.parse_args()
    if args.batch_size < 1 or not 1 <= args.workers <= 8 or not 1 <= args.quality <= 100:
        parser.error('batch-size must be positive, workers 1..8, quality 1..100')
    magick = shutil.which('magick')
    if not magick:
        parser.error('ImageMagick is required. Install it and make magick available on PATH.')
    DEST.mkdir(parents=True, exist_ok=True)
    # Exclusive lock prevents two helpers from processing the same outputs.
    lock = ROOT / 'scripts/webp-conversion.lock'
    try:
        lock_fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        parser.error('Another conversion is running. If it was forcibly terminated, remove scripts/webp-conversion.lock and retry.')
    os.close(lock_fd)
    try:
        state = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {}
        files = sorted((ROOT / 'assets/gallery').glob('*.jpg'))
        existing_webps = sum(not path.name.endswith('.tmp.webp') for path in DEST.glob('*.webp'))
        print(f'WebP library: {existing_webps} files | JPG sources: {len(files)}', flush=True)
        def current(path):
            stat = path.stat()
            entry = state.get(path.name, {})
            target = DEST / (path.stem + '.webp')
            return (entry.get('mtime_ns') == stat.st_mtime_ns and entry.get('source_bytes') == stat.st_size
                    and entry.get('quality') == args.quality and target.exists()
                    and entry.get('webp_bytes') == target.stat().st_size)
        pending = [path for path in files if not current(path)]
        selected = pending if args.all else pending[:args.batch_size]
        print(f'{len(files)} photos | {len(files)-len(pending)} ready | {len(pending)} pending | processing {len(selected)}', flush=True)
        failures = []
        def convert(path):
            target = DEST / (path.stem + '.webp')
            temporary = target.with_suffix('.tmp.webp')
            try:
                result = subprocess.run([magick, str(path), '-auto-orient', '-strip', '-quality', str(args.quality),
                    '-define', 'webp:method=4', '-write', str(temporary), '-format', '%w %h', 'info:'],
                    capture_output=True, text=True, timeout=120, check=True,
                    env={**os.environ, 'MAGICK_THREAD_LIMIT': '1'})
                width, height = map(int, result.stdout.strip().split())
                if not temporary.is_file() or temporary.stat().st_size == 0:
                    raise ValueError('Empty output')
                os.replace(temporary, target)
                stat = path.stat()
                return path.name, {'mtime_ns': stat.st_mtime_ns, 'source_bytes': stat.st_size,
                    'quality': args.quality, 'webp_bytes': target.stat().st_size, 'width': width, 'height': height}
            finally:
                temporary.unlink(missing_ok=True)
        started = time.monotonic()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for start in range(0, len(selected), args.batch_size):
                batch = selected[start:start + args.batch_size]
                futures = {pool.submit(convert, path): path for path in batch}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        name, entry = future.result()
                        state[name] = entry
                    except Exception as error:
                        name = futures[future].name
                        failures.append(name)
                        print(f'ERROR {name}: {error}', flush=True)
                temporary = STATE.with_suffix('.tmp.json')
                temporary.write_text(json.dumps(state, separators=(',', ':')), encoding='utf-8')
                os.replace(temporary, STATE)
                print(f'Batch {start//args.batch_size+1}: {min(start+len(batch),len(selected))}/{len(selected)} processed | {len(failures)} errors | {time.monotonic()-started:.0f}s', flush=True)
        # Catalog can serve converted photos while pending ones retain JPEG fallback.
        subprocess.run([sys.executable, str(ROOT / 'scripts/catalog.py')], check=True)
        subprocess.run([sys.executable, str(ROOT / 'scripts/version_assets.py'), '--force'], check=True)
        ready = [state[path.name] for path in files if current(path)]
        original_bytes = sum(entry['source_bytes'] for entry in ready)
        webp_bytes = sum(entry['webp_bytes'] for entry in ready)
        print(f'Ready: {len(ready)}/{len(files)} | JPG {original_bytes/1e6:.1f} MB -> WebP {webp_bytes/1e6:.1f} MB', flush=True)
        print(f'WebP gallery: {sum(not path.name.endswith(".tmp.webp") for path in DEST.glob("*.webp"))} files', flush=True)
        return 1 if failures else 0
    finally:
        lock.unlink(missing_ok=True)

if __name__ == '__main__':
    result = main()
    if result == 0 and '--delete-originals' in sys.argv:
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/verify_webp.py'), '--delete-originals']).returncode
    sys.exit(result)
