import os
import telebot
from telebot.types import Message, PhotoSize, Video, Document, Audio
import time
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = "your api key"
BOT_USERNAME = "your bot username"
POSTS_FILE = "posts.json"
ADMINS_FILE = "admins.json"

bot = telebot.TeleBot(API_KEY)

"""
{
    "post_id": {
        "name": "post name",
        "type": "text/photo/video/document/audio",
        "content": "text or file_id",
        "caption": "optional caption",
        "entities": [message entities for formatting],
        "caption_entities": [optional],
        "parse_mode": "HTML/MarkdownV2"
    }
}
"""

def load_data(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {} if filename == POSTS_FILE else []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {} if filename == POSTS_FILE else []

def save_data(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

posts = load_data(POSTS_FILE)
admins = load_data(ADMINS_FILE)
main_admin = "RealShadowSama"

def convert_entities_to_dict(entities):
    if not entities:
        return None
    return [{"type": e.type, "offset": e.offset, "length": e.length, "url": getattr(e, 'url', None)} for e in entities]

def extract_content(message: Message):
    content = {}

    if message.text:
        content = {
            "type": "text",
            "content": message.text,
            "entities": convert_entities_to_dict(message.entities),
            "parse_mode": "HTML"
        }
    elif message.caption:
        content = {
            "type": "media",
            "content": None,
            "caption": message.caption,
            "caption_entities": convert_entities_to_dict(message.caption_entities),
            "parse_mode": "HTML"
        }

        if message.photo:
            content.update({
                "type": "photo",
                "content": message.photo[-1].file_id
            })
        elif message.video:
            content.update({
                "type": "video",
                "content": message.video.file_id
            })
        elif message.document:
            content.update({
                "type": "document",
                "content": message.document.file_id
            })
        elif message.audio:
            content.update({
                "type": "audio",
                "content": message.audio.file_id
            })
    elif message.photo:
        content = {
            "type": "photo",
            "content": message.photo[-1].file_id
        }
    elif message.video:
        content = {
            "type": "video",
            "content": message.video.file_id
        }
    elif message.document:
        content = {
            "type": "document",
            "content": message.document.file_id
        }
    elif message.audio:
        content = {
            "type": "audio",
            "content": message.audio.file_id
        }

    return content if content else None

def send_post_content(chat_id, post_data):
    try:
        parse_mode = post_data.get("parse_mode")

        if post_data["type"] == "text":
            return bot.send_message(
                chat_id,
                post_data["content"],
                entities=post_data.get("entities") if post_data.get("entities") else None,
                parse_mode=None if post_data.get("entities") else parse_mode
            )
        elif post_data["type"] in ["photo", "video", "document", "audio"]:
            method = {
                "photo": bot.send_photo,
                "video": bot.send_video,
                "document": bot.send_document,
                "audio": bot.send_audio
            }[post_data["type"]]

            kwargs = {
                "chat_id": chat_id,
                post_data["type"]: post_data["content"]
            }

            if "caption" in post_data:
                kwargs.update({
                    "caption": post_data["caption"],
                    "caption_entities": post_data.get("caption_entities") if post_data.get("caption_entities") else None,
                    "parse_mode": None if post_data.get("caption_entities") else parse_mode
                })

            return method(**kwargs)
    except Exception as e:
        print(f"Error sending post: {e}")
        return None

def is_admin(user):
    username = user.username.lower() if user.username else None
    return username == main_admin.lower() or username in [a.lower() for a in admins]

@bot.message_handler(commands=['start', 'help'])
def handle_start(message: Message):
    args = message.text.split()

    if len(args) > 1:
        handle_post_request(message, args[1])
        return

    if is_admin(message.from_user):
        bot.reply_to(message,
                    "📝 Post Bot\n\n"
                    "✨ Features:\n"
                    "- Create posts by replying to a message with «Atomic : Create Post»\n"
                    "- Save various content (text, images, videos, files, audio)\n"
                    "- Share posts with direct links\n\n"
                    "🛠 Admin commands:\n"
                    "Atomic : Post List - Show all posts\n"
                    "Atomic : Add Admin - Add new admin\n\n"
                    "To create a new post, reply to a message with:\n"
                    "Atomic : Create Post")

def handle_post_request(message: Message, post_code):
    if post_code in posts:
        post_data = posts[post_code]
        msg = send_post_content(message.chat.id, post_data)

        if msg:
            countdown_msg = bot.send_message(message.chat.id, "⏳ This post will be deleted in 45 seconds.")
            time.sleep(45)
            try:
                bot.delete_message(message.chat.id, msg.message_id)
            except Exception as e:
                print(f"Error deleting message: {e}")
    else:
        bot.reply_to(message, "⚠️ Post not found!")

@bot.message_handler(func=lambda m: m.text.strip() == "Atomic : Post List")
def list_posts(message: Message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "⛔ Access Denied!")
        return

    if not posts:
        bot.reply_to(message, "ℹ️ No posts available.")
        return

    response = "📋 Post List:\n\n"
    for post_id, post_data in posts.items():
        post_link = f"https://t.me/{BOT_USERNAME}?start={post_id}"
        response += f"📌 {post_data.get('name', 'Untitled')}\n"
        response += f"🔗 {post_link}\n"
        response += f"──────────────────\n"

    bot.reply_to(message, response)

@bot.message_handler(func=lambda m: m.reply_to_message and m.text.strip().startswith("Atomic : Create Post"))
def create_new_post(message: Message):
    if not is_admin(message.from_user):
        bot.reply_to(message, "⛔ Access Denied!")
        return

    parts = message.text.split('\n')
    post_name = parts[1].strip() if len(parts) > 1 else f"Post {len(posts)+1}"

    replied_message = message.reply_to_message
    post_content = extract_content(replied_message)

    if not post_content:
        bot.reply_to(message, "⚠️ Unsupported message type!")
        return

    post_code = f"post_{len(posts)+1}_{int(time.time())}"
    post_content["name"] = post_name
    posts[post_code] = post_content
    save_data(POSTS_FILE, posts)

    post_link = f"https://t.me/{BOT_USERNAME}?start={post_code}"
    bot.reply_to(message, f"✅ Post saved successfully!\n\n"
                         f"📝 Post name: {post_name}\n"
                         f"🔗 Direct link:\n"
                         f"{post_link}\n\n"
                         f"Or use this command:\n"
                         f"/start {post_code}")

@bot.message_handler(func=lambda m: m.reply_to_message and m.text.strip() == "Atomic : Add Admin")
def add_admin(message: Message):
    if str(message.from_user.username).lower() != main_admin.lower():
        bot.reply_to(message, "⛔ Only the bot owner can add admins!")
        return

    replied_message = message.reply_to_message
    if not replied_message.text or replied_message.text.startswith('@'):
        bot.reply_to(message, "⚠️ Please reply to a text message containing the username (without @).")
        return

    new_admin = replied_message.text.strip()
    if new_admin.lower() in [a.lower() for a in admins] or new_admin.lower() == main_admin.lower():
        bot.reply_to(message, "⚠️ This user is already an admin!")
        return

    admins.append(new_admin)
    save_data(ADMINS_FILE, admins)
    bot.reply_to(message, f"✅ @{new_admin} has been added to admin list successfully!")

if __name__ == "__main__":
    print("Loading...")
    print("Enabled")
    bot.polling()