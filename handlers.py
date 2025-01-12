import os

import aiofiles
from aiogram import types

from services import send_file_and_metadata, send_text_params
from settings import AUTHORIZED_USERS, AUTHORIZED_PATH, UNAUTHORIZED_PATH


async def handle_document(message: types.Message):
    user_id = str(message.from_user.id)
    file_id = message.document.file_id
    file_name = message.document.file_name
    description = message.caption

    # Получаем файл
    file = await message.bot.get_file(file_id)
    file_path = file.file_path
    download_dir = AUTHORIZED_PATH if str(user_id) in AUTHORIZED_USERS else UNAUTHORIZED_PATH
    os.makedirs(download_dir, exist_ok=True)
    destination_full_path = os.path.join(download_dir, file_name)

    # Если пользователь в белом списке
    if str(user_id) in AUTHORIZED_USERS:
        await message.bot.download_file(file_path, destination=destination_full_path)
        # await send_metadata_to_rabbitmq(user_id=user_id, username=message.from_user.username, description=description)
        # await send_file_to_rabbitmq(
        #     file_path=destination_full_path,
        # )
        result = await send_file_and_metadata(
            file_path=destination_full_path,
            user_id=user_id,
            username=message.from_user.username,
            description=description
        )
        await message.reply(result)
    else:
        # Обработка неавторизованных пользователей
        await message.bot.download_file(file_path, destination_full_path)

        async with aiofiles.open(f'{destination_full_path}.txt', 'w') as f:
            await f.write(f'ID: {user_id}, Name: {message.from_user.username}, message: {description}\n')

        await message.reply("Вы не авторизованы для отправки файлов. Ваш файл сохранён.")


async def handle_text(message: types.Message):
    received_text = message.text
    # Проверяем, есть ли в сообщении необходимые параметры
    if all(param in received_text for param in ['t=', 's=', 'fn=', 'i=', 'fp=', 'n=']):
        user_id = str(message.from_user.id)
        await send_text_params(user_id=user_id, username=message.from_user.username, description=received_text)
        await message.reply("Параметры чека успешно отправлены на обработку.")
    else:
        await message.reply(
            "Формат сообщения некорректен. Пожалуйста, убедитесь, что сообщение содержит все необходимые параметры.")


async def handle_other(message: types.Message):
    print(message)
