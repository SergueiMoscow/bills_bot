from datetime import datetime
import json
import os

import aio_pika
import aiofiles
import grpc

import file_service_pb2
import file_service_pb2_grpc
from settings import RABBITMQ_URL, BILLS_SERVICE_TOKEN, BILLS_SERVICE_URL


async def send_file_to_rabbitmq(file_path: str):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()

        async with aiofiles.open(file_path, 'rb') as file:
            file_content = await file.read()

        await channel.default_exchange.publish(
            aio_pika.Message(body=file_content),
            routing_key='file_queue',
        )

    print(f'Sent file: {file_path}')

async def send_metadata_to_rabbitmq(user_id: str, username: str, description: str):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()

        message_data = {
            "user_id": user_id,
            "username": username,
            "description": description
        }

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message_data).encode()),
            routing_key='metadata_queue',
        )

    print(f'Sent metadata for user: {user_id}')

async def send_file_and_metadata(
    file_path: str,
    user_id: str,
    username: str,
    description: str
) -> str:
    channel = grpc.aio.insecure_channel(BILLS_SERVICE_URL)
    stub = file_service_pb2_grpc.FileServiceStub(channel)

    # Чтение файла в байты
    with open(file_path, 'rb') as f:
        file_content = f.read()

    request = file_service_pb2.UploadFileRequest(
        file=file_content,
        user_id=user_id,
        username=username,
        description=description,
        filename=os.path.basename(file_path),
        token=BILLS_SERVICE_TOKEN,
    )

    response = await stub.UploadFile(request)
    print(response.message)

    await channel.close()
    return response.message


async def send_text_params(user_id: str, username: str, description: str) -> str:
    channel = grpc.aio.insecure_channel(BILLS_SERVICE_URL)
    stub = file_service_pb2_grpc.FileServiceStub(channel)

    filename = f'bill_{user_id}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.txt'
    request = file_service_pb2.UploadFileRequest(
        file=description.encode('utf-8'),  # Преобразуем текст в байты
        user_id=user_id,
        username=username,
        description=description,
        filename=filename,
        token=BILLS_SERVICE_TOKEN,
    )

    response = await stub.UploadFile(request)
    print(response.message)

    await channel.close()
    return response.message