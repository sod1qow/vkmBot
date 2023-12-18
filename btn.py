from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def songs_btn(song_list, count_songs):
    btn = InlineKeyboardMarkup(row_width=5)

    btn.add(
        *[InlineKeyboardButton(text=f"{num}", callback_data=f"song:{item[0]}") for num, item in enumerate(song_list, start=1)]
    )

    if count_songs > 10:
        btn.row(
            InlineKeyboardButton(text="⬅️", callback_data="prev_list"),
            InlineKeyboardButton(text="➡️", callback_data="next_list"),
        )

    return btn





async def admin_panel_btn():
    btn = InlineKeyboardMarkup(row_width=2)
    btn.add(
        InlineKeyboardButton(text="Kanal ➕", callback_data="add_channel"),
        InlineKeyboardButton(text="Xabar yo`llash", callback_data="mailing"),
        InlineKeyboardButton(text="Statistika", callback_data="stat"),
    )
    return btn



async def add_channel_btn(channels):
    btn = InlineKeyboardMarkup(row_width=1)
    btn.add(
        InlineKeyboardButton(text="➕", callback_data="create_channel"),
        InlineKeyboardButton(text="Ortga", callback_data="back"),
    )

    if channels:
        for item in channels:
            btn.add(
                InlineKeyboardButton(text=f"{item[1]}", callback_data=f"channel:{item[3]}")
            )

    return btn