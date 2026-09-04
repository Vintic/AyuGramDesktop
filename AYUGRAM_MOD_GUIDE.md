# AyuGram Custom Modifications Guide

This guide documents the custom modifications made to this branch of AyuGram, including dynamic settings syncing, custom Instant View previews, build automation, and testing tools.

## 1. Dynamic Settings via Saved Messages

AyuGram usually loads settings from disk. To make it easier to configure custom previews dynamically across multiple devices without touching config files, we added a feature that parses settings directly from a message in your **Saved Messages**.

### How it Works
1. When the app starts, it fetches your Saved Messages history.
2. It looks for a message starting with `#ayugram_settings`.
3. It parses the JSON payload inside that message.
4. It sets up a real-time listener: if you edit that message while the app is running, the settings automatically apply instantly without needing an app restart!

### Example Configuration Message
Send the following message to your **Saved Messages**:

```json
#ayugram_settings
{
  "link_previews": {
    "twitter.com": "fixupx.com",
    "x.com": "fixupx.com",
    "tiktok.com": "kktiktok.com",
    "reddit.com": "vxreddit.com",
    "instagram.com": "kkclip.com",
    "pixiv.net": "phixiv.net"
  },
  "instant_view": {
    "999.md": "1b047efddd1e39"
  }
}
```

- `link_previews`: A dictionary mapping original hostnames to replacement hostnames for better server-side previews (e.g., swapping `twitter.com` for `fixupx.com`).
- `instant_view`: A dictionary mapping hostnames to their respective Telegram Instant View `rhash` codes.

**Wildcard Masks Supported:**
You can use a wildcard prefix (`*.`) in your JSON keys to match a domain and all of its subdomains! For example, using `*.twitter.com` will automatically apply the rule to `twitter.com`, `www.twitter.com`, `m.twitter.com`, etc.

## 2. Link Previews (Hostname Substitution)

Some platforms (like Twitter/X, Reddit, or TikTok) block or break Telegram's native link preview scrapers. The community has created alternative frontends (like `fixupx.com` or `vxreddit.com`) that properly return video and image metadata.

### How it works
If you send a link like `https://twitter.com/AyuGram`, the app intercepts the link before generating a preview.
1. It checks the `link_previews` map.
2. It sees that `twitter.com` maps to `fixupx.com`.
3. It quietly swaps the domain in the preview request, so Telegram's servers scrape `fixupx.com` instead.
4. The recipient still sees the original `twitter.com` text in the message, but with the beautiful, fixed rich media preview attached!

## 3. Instant View Previews

Telegram allows "Instant View" (IV) pages to load articles instantly inside the app. Normally, this only works for officially supported websites.

### How we bypassed it
When you type a URL (like `999.md`), AyuGram intercepts it and checks your `iv_rules`. 
If a match is found:
1. It resolves the internal Instant View URL: `https://t.me/iv?rhash=...&url=...`
2. **The Magic Trick**: Because the Telegram API strictly rejects sending `t.me/iv` links inside the `InputMediaWebPage` object during `SendMedia` requests (throwing a `WEBPAGE_NOT_FOUND` error), we gracefully convert the request to a regular `SendMessage` request.
3. We insert a completely invisible zero-width space character (`\u200B`) at the very **beginning** of your message.
4. We shift the offsets of all your existing formatting entities by +1 so we don't break your bold/italic/links.
5. We attach a `MessageEntityTextUrl` specifically to that invisible character at the beginning, pointing it to the `t.me/iv` link.
6. The Telegram server natively discovers the hidden `t.me/iv` link first and automatically attaches the Instant View preview to your message.

## 3. Automation Scripts

### `build_ayugram.sh`
This script automates the tedious process of building and testing AyuGram. It bridges your local Git repository with the Arch Linux `yay` build system.

**Usage:**
```bash
./build_ayugram.sh
```

**What it does:**
1. Generates a single `.patch` file of all your local commits relative to `origin/dev`.
2. Copies the patch to the AUR package directory (`~/.cache/yay/ayugram-desktop`).
3. Compiles the package in the background (`makepkg -f`).
4. Kills the currently running instance of AyuGram *only after* compilation is complete, so you can keep chatting while it compiles!
5. Asks if you want to install it system-wide via `sudo pacman -U`.
6. Launches the newly built app.

### `test_instant_view.py`
This is a standalone Python script utilizing `Telethon` to test raw MTProto API calls without having to recompile the entire C++ application. It's incredibly useful for reverse-engineering Telegram's strict API requirements.

**Setup:**
1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` and insert your `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org).
3. Set up the Python environment:
   ```bash
   python3 -m venv test_env
   source test_env/bin/activate
   pip install telethon
   ```

**Running the test:**
```bash
python test_instant_view.py
```
It will ask for your phone number and Telegram login code the first time you run it. It will then attempt to send a message to your Saved Messages using the exact MTProto method we implemented, allowing you to instantly verify if the Telegram server accepts or rejects the payload.
