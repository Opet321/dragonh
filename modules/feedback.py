from asyncio import sleep  
from time import sleep 
from pyrogram import Client, filters 
from pyrogram.types import Message  
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from naya.config import MONGO_URL, OWNER 
from . import * 
 
cli = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL) 
users = db.users  
mongo = MongoCli(MONGO_URL) 
messages = db.messages 
 
 
async def _message_id(message_id): 
 message_id = await messages.find_one({"forward_id": f"{message_id}"}) 
 return message_id 


@app.on_message(filters.command("start"))
async def _start(client: Client, message: Message):
    user_db = await users.find_one({"user_id": f"{message.from_user.id}"})
    if not user_db:
        user_id = {"user_id": f"{message.from_user.id}"}
        await users.insert_one(user_id)
        
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("AnonXMusikbot", url="https://t.me/anonxmusikbot"),
                    InlineKeyboardButton("SaitamaXbot", url="https://t.me/saitamaxbot")
                ]
            ]
        )
        
        await client.send_message(message.chat.id, f"<b>Hello, {message.from_user.mention}!</b>\n\n<b>Saya Merekomendasikan BOT Music yang Aktif & BOT Group Management</b>\n\n<b>Bila ada Gangguan Terhadap BOT bisa langsung hubungi owner, kirim pesan lu disini nanti ku teruskan pesan nya</b>", reply_markup=keyboard)
    else:
        await message.reply_text("<b>Kirim saya pesan Anda dan saya akan meneruskannya!</b>", reply_to_message_id=message.id)
 
 
 
@app.on_message(filters.chat(int(OWNER))) 
async def _owner(client: Client, message: Message): 
    last_msg = None  # Memberikan nilai awal untuk last_msg 
    async for msg in messages.find(): 
        last_msg = msg 
 
    if message.reply_to_message: 
        message_id = await _message_id(message.reply_to_message.id) 
        if message_id: 
            await message.copy(int(message_id['user_id']), reply_to_message_id=int(message_id['message_id'])) 
            await message.reply_text(f"<b>Pesan Anda telah terkirim ke {(message_id['user_id'])}</b>", reply_to_message_id=message.id, disable_notification=True) 
            if last_msg and int(last_msg['user_id']) != int(message_id['user_id']): 
                message_data = { 
                    "forward_id": f"{message_id['forward_id']}", 
                    "message_id": f"{message_id['message_id']}", 
                    "user_id": f"{message_id['user_id']}" 
                } 
                await messages.insert_one(message_data) 
            await asyncio.sleep(5) 
            await message.delete() 
    else: 
        if last_msg: 
            message_id = await _message_id(last_msg['forward_id']) 
            if message_id: 
                await message.copy(int(message_id['user_id'])) 
                await message.reply_text(f"<b>Pesan Anda telah terkirim ke {(message_id['user_id'])}</b>", reply_to_message_id=message.id, disable_notification=True) 
                await asyncio.sleep(5) 
                await message.delete() 
        else: 
            await message.reply_text("List is empty, cannot retrieve last message.") 
 
 
@app.on_message(filters.all & filters.private & ~filters.me) 
async def _user(client: Client, message: Message): 
    user_db = await users.find_one({"user_id": f"{message.from_user.id}"}) 
    if not user_db: 
        await message.reply_text(f"<b>You are not in the database, enter /start to use the bot!</b>", reply_to_message_id=message.id) 
    else: 
        forwarded_message = await message.forward(OWNER) 
        message_data = {"forward_id": f"{forwarded_message.id}", 
                        "message_id": f"{message.id}", 
                        "user_id": f"{message.from_user.id}"} 
        await messages.insert_one(message_data) 
        message = await message.reply_text(f"Pesan Anda Telah Terkirim", reply_to_message_id=message.id, disable_notification=True) 
        await asyncio.sleep(3) 
        await message.delete()