#!/usr/bin/env bash
# Zip the extension for the Chrome Web Store or sharing.
set -euo pipefail
cd "$(dirname "$0")/.."
version=$(python3 -c "import json;print(json.load(open('extension/manifest.json'))['version'])")
mkdir -p dist
out="dist/canva-button-hider-v${version}.zip"
rm -f "$out"
(cd extension && zip -qr "../$out" . -x '*.DS_Store')
echo "Built $out"
