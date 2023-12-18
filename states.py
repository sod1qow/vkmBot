from aiogram.dispatcher.filters.state import StatesGroup, State




class AdminPanelStates(StatesGroup):
    create_channel_state = State()
    mailing = State()
    create_category_state = State()

