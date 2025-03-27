import os
import subprocess
from aiogram import Bot, F
from aiogram import Router


from aiogram.types import Message


API_TOKEN = '8021931800:AAHReyFve0oalMPsHVzPsPrl2Wl239XF724'  # Replace with your actual bot token

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
router = Router()





@router.message(F.command('start'))
async def start_command(message: Message):



    await message.reply("Запускаю приложение...")
    # Launch the Streamlit app
    subprocess.Popen(['streamlit', 'run', 'main.py'])
    await message.reply("Приложение запущено! Откройте браузер для доступа.")

# Start polling (without executor)
if __name__ == '__main__':
    import asyncio
    from aiogram import Dispatcher

    dp = Dispatcher()
    dp.include_router(router)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dp.start_polling(bot))
