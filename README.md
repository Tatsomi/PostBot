# Shadow Sama Post Bot

A Telegram bot for managing and sharing posts with support for multimedia content and user-friendly links.

made by Tatsomi

### My Telegram ID : @RealShadowSama

=============================

## Features

- Create and store posts by replying to a message with "Atomic : Create Post"
- Supports text, images, videos, documents, audio
- Generate sharable links for each post (/start POST_ID)
- Telegram formatting and entity support (bold, italic, etc.)
- Admin-only commands and access control
- Simple and extensible structure

=============================

## Setup

1. Clone the repo:
   git clone https://github.com/Tatsomi/ShadowSamaPostBot.git
   cd ShadowSamaPostBot

2. Install dependencies:
   pip install -r requirements.txt

3. Run the bot:
   python bot.py

=============================

## Admin Commands

- Atomic : Create Post (reply to a message) → Save that message as a post
- Atomic : Post List → Show all saved posts with links
- Atomic : Add Admin (reply to a text with username) → Add new admin (only main admin can)

=============================

## Post Format (posts.json)

{
  "post_1_1713798450": {
    "name": "My Post Title",
    "type": "text/photo/video/document/audio",
    "content": "text or file_id",
    "caption": "optional caption",
    "entities": [],
    "caption_entities": [],
    "parse_mode": "HTML"
  }
}

=============================

## Main Admin

Set the main admin username in `bot.py` under the `main_admin` variable.
Only this user can add other admins.

=============================

## Files

- bot.py → Main bot script
- posts.json → Saved post content
- admins.json → List of admins
- .env → Your API token (not committed)

=============================

## License

MIT License
