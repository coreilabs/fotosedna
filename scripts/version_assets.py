"""Run before publishing to refresh asset URLs when their contents change."""
import hashlib
import argparse
import re
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--force', action='store_true', help='Renew all versions even when contents are unchanged.')
args = parser.parse_args()
release = secrets.token_hex(6) if args.force else ''

def version(path):
    return hashlib.sha256((ROOT / path).read_bytes() + release.encode()).hexdigest()[:12]

app = ROOT / 'assets/app.js'
source = app.read_text(encoding='utf-8')
source = re.sub(
    r"\./vendor/photoswipe\.esm\.min\.js(?:\?v=[a-zA-Z0-9-]+)?",
    './vendor/photoswipe.esm.min.js?v=' + version('assets/vendor/photoswipe.esm.min.js'),
    source,
)
app.write_text(source, encoding='utf-8')

html = ROOT / 'index.html'
source = html.read_text(encoding='utf-8')
for asset in ('assets/style.css', 'assets/vendor/photoswipe.css', 'assets/app.js'):
    source = re.sub(re.escape(asset) + r'(?:\?v=[a-zA-Z0-9-]+)?', asset + '?v=' + version(asset), source)
html.write_text(source, encoding='utf-8')
print('Asset URLs updated from content hashes.')
