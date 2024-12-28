import os
import logging

from pathlib import Path

from pyrogram import Client, idle, errors
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.raw.functions.account import DeleteAccount

from utils.database import db
from utils.loader import _loader
from utils.helpers.updater import restart
from utils.config import (
    api_id,
    api_hash,
    bot_token,
    session_string,
    version
)

script_path = os.path.dirname(os.path.realpath(__file__))
if script_path != os.getcwd():
    os.chdir(script_path)

# Client Bot
bot = Client(
    name="Feedback",
    api_id=api_id,  # Gunakan api_id dari config
    api_hash=api_hash,  # Gunakan api_hash dari config
    bot_token=bot_token,
    in_memory=True,
    sleep_threshold=30,
    plugins=dict(root="plugins"),
    parse_mode=ParseMode.HTML
)

# Client Pengguna
app = Client(
    "Dragon-Fork",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string,
    workdir=script_path,
    device_model=version,
    sleep_threshold=30,
    parse_mode=ParseMode.HTML,
)

async def main():
    logging.basicConfig(level=logging.INFO)
    DeleteAccount.new = None

    try:
        await app.start()  # Mulai client pengguna
        await bot.start()  # Mulai client bot
    except (errors.NotAcceptable, errors.Unauthorize) as e:
        logging.error(
            f"{e.class.name}: {e}\n"
            )
        restart()

    success_modules = 0
    failed_modules = 0

    for path in Path("modules").glob("*.py"):
        try:
            await _loader(path.stem, app, core="custom_modules" not in path.parent.parts
            )
        except Exception:
            logging.warning(
                f"Can't import module {path.stem}!",
                exc_info=True
            )
            failed_modules += 1
        else:
            success_modules += 1

    logging.info(
        f"Imported {success_modules} modules!"
    )
    if failed_modules:
        logging.warning(
            f"Failed to import {failed_modules} modules!"
        )

    if info := db.get("core.updater", "restart_info"):
        text = {
            "restart": "Restart completed!",
            "update": "Update process completed!",
        }[info["type"]]
        try:
            await app.edit_message_text(  # Menggunakan app untuk mengedit pesan
                info["chat_id"], info["message_id"], text
            )
        except errors.RPCError:
            pass
        db.remove("core.updater", "restart_info")

    logging.info("Dragon-Fork started!")
    await app.send_message("me", "Started!")  # Menggunakan app untuk mengirim pesan
    await bot.send_message("me", "Bot Started!") # Menggunakan bot untuk mengirim pesan

    await idle()
    await app.stop() # stop app
    await bot.stop()  # Stop bot

if __name__ == "__main__":
    app.run(main())
