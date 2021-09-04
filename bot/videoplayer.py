import os
import asyncio
from pytgcalls import GroupCallFactory
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import API_ID, API_HASH, SESSION_NAME, BOT_USERNAME, THUMB_URL
from helpers.decorators import authorized_users_only
from helpers.filters import command

thumb =THUMB_URL
app = Client(SESSION_NAME, API_ID, API_HASH)
group_call_factory = GroupCallFactory(app, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)
VIDEO_CALL = {}

buttons = [
            [
                InlineKeyboardButton("Mute ", callback_data="vmute"),
                InlineKeyboardButton("Unmute ", callback_data="vunmute"),
            ],
            [
                InlineKeyboardButton("End", callback_data="vend"),
            ]
]
caption =f"💡 **video streaming started!**\n\n» **join to video chat to watch the video."

@Client.on_message(command(["vstream", f"vstream@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stream(client, m: Message):
    replied = m.reply_to_message
    if not replied:
        await m.reply("💭 **Give me a video to stream**\n\n» Use the /vstream command by replying to the video.")
    elif replied.video or replied.document:
        file = replied.video or replied.document
        types = file.mime_type.split("/")
        mime = types[0]
        if mime == "video":
        	msg = await m.reply("📥 **downloading video...**\n\n💭 __this process will take quite a while depending on the size of the video.__")
        	chat_id = m.chat.id
        	try:
        	   video = await client.download_media(m.reply_to_message)
        	   await msg.edit("⏳ **Converting video...**")
        	   os.system(f'ffmpeg -i "{video}" -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le -filter:a "atempo=0.81" vid-{chat_id}.raw -y')
        	except Exception as e:
        		await msg.edit(f"**🚫 Error** - `{e}`")
        		await asyncio.sleep(5)
        	try:
        	   group_call = group_call_factory.get_file_group_call(f'vid-{chat_id}.raw')
        	   await group_call.start(chat_id)
        	   await group_call.set_video_capture(video, repeat=False)
        	   VIDEO_CALL[chat_id] = group_call
        	   await msg.reply_photo(thumb,caption=caption,reply_markup=buttons)
        	except Exception as e:
        		print(f"ERROR:\n{str(e)}")
        else:
        	await m.reply(f"🔺**how can i play {mime} ?, please reply to a video or video file** ")
    else:
        await m.reply("🔺 **please reply to a video or video file!**")


@Client.on_message(command(["vstop", f"vstop@{BOT_USERNAME}"]) & filters.group & ~filters.edited)
@authorized_users_only
async def stopvideo(client, m: Message):
    chat_id = m.chat.id
    try:
        await VIDEO_CALL[chat_id].stop()
        await m.reply("🔴 **streaming has ended !**\n\n✅ __userbot has been disconnected from the video chat__")
    except Exception as e:
        await m.reply(f"**🚫 Error** - `{e}`")
