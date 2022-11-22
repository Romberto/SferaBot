from aiogram import types, Dispatcher
import bcrypt

from database.token_db import get_token, token_finaly
from keyboard.driver_kb import kb_drivers
from keyboard.token_active_kb import kb_tokens
from states import ActivateTokenState, ReportState
from aiogram.dispatcher import FSMContext


# отслеживает нажатие на кнопку Проверить токен или Отчёт за сегодня
async def token_get(message: types.Message, state=FSMContext):
    if message.text == 'Проверить код':
        await ActivateTokenState.next()
        await message.answer('Отправте токен экскурсии')
    elif message.text == 'Отчёт за сегодня':
        await state.finish()
        # await report_today()
        await message.answer('отчёты пока в разработке')
        await ReportState.start.set()


async def check_token(message: types.Message, state=FSMContext):
    token_text = message.text
    token = await get_token(token_text)
    if token:
        await state.update_data(token=token_text)
        await message.reply('Экскурсия ' + token.excursion_name + '\nцена: ' + token.excursion_price + '',
                            reply_markup=kb_tokens)
        await ActivateTokenState.next()
    else:
        await message.reply('активных токенов с таким кодом не найдено')


async def active_token(message: types.Message, state=FSMContext):
    if message.text == 'Активировать':

        kb_enroll = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(text='ДА', callback_data='yes'),
            types.InlineKeyboardButton(text='НЕТ', callback_data='no')
        ]
        kb_enroll.add(*buttons)
        await message.answer("Активировать, \nВы уверены ? ", reply_markup=kb_enroll)
        await ActivateTokenState.next()
    elif message.text == 'Назад':
        await message.answer("С помощью кнопки 'проверить код', активируйте экскурсию", reply_markup=kb_drivers)
        await ActivateTokenState.start.set()


async def token_finish(call: types.CallbackQuery, state=FSMContext):
    if call.data == 'yes':
        await call.message.answer('Активирую')
        data = await state.get_data()
        token = data['token']
        driver = data['driver_id']
        await token_finaly(token, str(driver))
        await call.message.answer("С помощью кнопки 'проверить код', активируйте экскурсию", reply_markup=kb_drivers)
        await ActivateTokenState.start.set()
    elif call.data == 'no':
        await call.answer('назад', cache_time=3)
        await call.message.answer("С помощью кнопки 'проверить код', активируйте экскурсию", reply_markup=kb_drivers)
        await ActivateTokenState.start.set()


async def token_error(message: types.Message):
    await message.answer("Извените я не понимаю")


def register_handlers_token(dp: Dispatcher):
    dp.register_message_handler(token_get, state=ActivateTokenState.start, content_types=['text'],
                                text=['Проверить код', 'Отчёт за сегодня'])
    dp.register_message_handler(check_token, state=ActivateTokenState.token, content_types=['text'])
    dp.register_message_handler(active_token, state=ActivateTokenState.token_active, content_types=['text'])
    dp.register_callback_query_handler(token_finish, state=ActivateTokenState.token_finish)
    dp.register_message_handler(token_error, content_types=['text'], state='*')
