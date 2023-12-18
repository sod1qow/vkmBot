import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Command

from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from database import *
from btn import *
from states import *
from config import BOT_TOKEN, ADMINS

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, parse_mode='html')
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)


async def command_menu(dp: Dispatcher):
    await dp.bot.set_my_commands(
        [
            types.BotCommand('start', 'Ishga tushirish'),
        ]
    )
    await create_tables()


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    await add_user(user_id=message.from_user.id)
    await message.answer("Menga xoxlagan qo`shiq nomini yoki ijrochisini yozing:")


@dp.message_handler(content_types=['audio'])
async def get_admin_audio_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id in ADMINS:
        audio_id = message.audio.file_id
        audio_title = message.audio.title if message.audio.title != "<unknown>" else None
        audio_subtitle = message.audio.performer if message.audio.performer != "<unknown>" else None
        await add_song(audio_id, audio_title, audio_subtitle)

        await message.answer("✅ Qo`shiq sqlandi")


@dp.callback_query_handler(text_contains="song")
async def send_song_to_user_callback(call: types.CallbackQuery):
    await call.answer()
    song_id = call.data.split(":")[-1]
    audio = await get_song_by_id(song_id)  # (1, title, subtitle, file_id)
    await call.message.answer_audio(audio[-1], title=audio[1], performer=audio[2])





@dp.message_handler(commands=['admin'])
async def admin_panel_command(message: types.Message):
    user_id = message.from_user.id

    if user_id in ADMINS:
        btn = await admin_panel_btn()
        await message.answer("Siz admin paneldasiz:", reply_markup=btn)


@dp.callback_query_handler(text="back")
async def back_to_panel_callback(call: types.CallbackQuery):
    btn = await admin_panel_btn()
    await call.message.edit_text("Siz admin paneldasiz:", reply_markup=btn)


@dp.callback_query_handler(text="add_channel")
async def add_channel_callback(call: types.CallbackQuery):
    channels = await get_channels()
    btn = await add_channel_btn(channels)
    await call.message.edit_text("Kanal qo`shish bo`limi:", reply_markup=btn)




@dp.callback_query_handler(text="stat")
async def show_bot_statistics_callback(call: types.CallbackQuery):
    users = await count_all_users()
    await call.answer(f"Bot azolari soni: {users}", show_alert=True)


@dp.callback_query_handler(text='mailing')
async def mailing_callback(call: types.CallbackQuery):
    await call.message.edit_text("Xabaringizni yuboring:")
    await AdminPanelStates.mailing.set()



@dp.message_handler(content_types=['text', 'photo', 'video', 'animation', 'document'], state=AdminPanelStates.mailing)
async def mailing_state(message: types.Message, state: FSMContext):
    text = message.html_text
    caption = message.html_text
    btn = message.reply_markup
    content = message.content_type
    users = await get_all_users()

    await state.finish()

    for user in users:

        if content == 'text':
            await bot.send_message(chat_id=user[1], text=text, reply_markup=btn)

        elif content == 'photo':
            await bot.send_photo(chat_id=user[1], photo=message.photo[-1].file_id, caption=caption, reply_markup=btn)

        elif content == 'video':
            await bot.send_video(chat_id=user[1], video=message.video.file_id, caption=caption, reply_markup=btn)

        elif content == 'animation':
            await bot.send_animation(chat_id=user[1], animation=message.animation.file_id, caption=caption,
                                     reply_markup=btn)

        elif content == 'document':
            await bot.send_document(chat_id=user[1], document=message.document.file_id, caption=caption,
                                    reply_markup=btn)

    await message.reply("✅ Xabar barchaga yo`llandi")
    await admin_panel_command(message)




@dp.callback_query_handler(text="next_list")
async def next_list_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    songs, count_songs = await search_song(data['text'], offset=data['offset'])
    current_song = (data['offset'] + len(songs))
    
    if current_song != count_songs:
        await state.update_data(offset=data['offset'] + 10)

    context = f"Topildi: {current_song}-{count_songs} Jami: {count_songs}\n\n"
    for num, item in enumerate(songs, 1):
        context += f"{num}) {item[1]} - {item[2]}\n"

    try:
        btn = await songs_btn(songs, count_songs)
        await call.message.edit_text(context, disable_web_page_preview=True, reply_markup=btn)
    except:
        pass




@dp.callback_query_handler(text="prev_list")
async def next_list_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data['offset'] == 10:
        offset = 1
    else:
        offset = 20
    songs, count_songs = await search_song(data['text'], offset=offset)

    if data['offset'] > 10:
        await state.update_data(offset=data['offset'] - 10)

    context = f"Topildi: {data['offset'] - 10}-{count_songs} Jami: {count_songs}\n\n"
    for num, item in enumerate(songs, 1):
        context += f"{num}) {item[1]} - {item[2]}\n"

    try:
        btn = await songs_btn(songs, count_songs)
        await call.message.edit_text(context, disable_web_page_preview=True, reply_markup=btn)
    except:
        pass




@dp.message_handler(content_types=['text'])
async def get_user_text_handler(message: types.Message, state: FSMContext):
    text = message.text
    data, count_songs = await search_song(text)

    if data:
        context = f"Topildi: 1-{len(data)} Jami: {count_songs}\n\n"

        for num, item in enumerate(data, 1):
            context += f"{num}) {item[1]} - {item[2]}\n"

        btn = await songs_btn(data, count_songs)
        await message.answer(context, disable_web_page_preview=True, reply_markup=btn)
        
        await state.update_data(offset=1, current_songs=len(data), text=text)

    else:
        await message.reply("Afsuski siz izlagan qo`shiq topilmadi 😔")








if __name__ == "__main__":
    executor.start_polling(dp, on_startup=command_menu)
