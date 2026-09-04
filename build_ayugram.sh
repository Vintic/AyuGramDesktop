#!/bin/bash

# Stop on errors
set -e

echo "📦 Generating single patch file from all branch commits..."
# This takes all commits from origin/dev to HEAD and combines them into one patch file
# This allows you to keep multiple commits in your branch without breaking the PKGBUILD!
git format-patch origin/dev..HEAD --stdout > ~/.cache/yay/ayugram-desktop/0003-dynamic-link-previews.patch

echo "🧹 Cleaning previous build cache..."
cd ~/.cache/yay/ayugram-desktop
rm -rf src

echo "🔨 Building AyuGram (this will take a while)..."
# Just build, don't install yet
makepkg -f --noconfirm

echo "🛑 Stopping currently running AyuGram..."
killall AyuGram || true
killall AyuGram-dev || true

echo "📦 Build complete! Do you want to install the package system-wide? (y/n)"
read -r install_choice
if [[ "$install_choice" =~ ^[Yy]$ ]]; then
    # Find the newly generated package file
    PKG_FILE=$(ls -t ayugram-desktop-*.pkg.tar.zst | head -n 1)
    echo "Installing $PKG_FILE..."
    sudo pacman -U "$PKG_FILE"
fi

echo "🚀 Starting AyuGram..."
if [[ "$install_choice" =~ ^[Yy]$ ]]; then
    # Run the system-installed version
    nohup ayugram-desktop >/dev/null 2>&1 &
else
    # Copy the locally built version to a stable location
    mkdir -p ~/.local/bin
    cp ~/.cache/yay/ayugram-desktop/pkg/ayugram-desktop/usr/bin/AyuGram ~/.local/bin/AyuGram-dev
    # Run the locally built version from the stable location
    nohup ~/.local/bin/AyuGram-dev >/dev/null 2>&1 &
fi
disown

# Wait briefly and verify if it started successfully
sleep 2
if pgrep -x "AyuGram" > /dev/null || pgrep -x "ayugram-desktop" > /dev/null || pgrep -x "AyuGram-dev" > /dev/null; then
    echo "✅ AyuGram successfully started in the background!"
else
    echo "❌ ERROR: AyuGram failed to start! You can try running it manually to see errors."
    exit 1
fi
