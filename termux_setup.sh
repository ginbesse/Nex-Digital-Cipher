#!/usr/bin/env sh
set -eu

echo "Termux için Python ve temel araçları kuruyorum..."

pkg update -y
pkg install -y python git curl openssl-tool

python3 --version

echo ""
echo "Kurulum tamamlandı."
echo "Kullanım:"
echo "  python3 smart_device_generator.py"
echo "  python3 smart_device_generator.py --demo"
