from urllib.parse import urlencode, urljoin

import aiohttp
import logging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession

from src.app.settings import settings
from src.app.api.routers.telegram_bot_routers import telegram_router

session = None
if settings.PROXY_URL:
    session = AiohttpSession(proxy=settings.PROXY_URL)
    logging.info(f"Using proxy: {settings.PROXY_URL}")
bot_token = settings.BOT
telegram_bot = Bot(token=bot_token, session=session)

external_api_url = settings.EXTERNAL_API_URL
telegram_bot_dispatcher = Dispatcher(storage=MemoryStorage())
telegram_bot_dispatcher.include_router(telegram_router)


@telegram_bot_dispatcher.callback_query(lambda c: c.data and c.data.startswith("order"))
async def handle_order_callback(callback_query: types.CallbackQuery):
    """Обрабатывает нажатие кнопки для подтверждения/отмены заказа."""
    callback_data = callback_query.data

    try:
        action, order_id = callback_data.split(":", 1)
    except ValueError:
        await callback_query.answer("Некорректный формат данных")
        return

    if action == "order_confirm":
        status = "IN_PROGRESS"
        message = "Вы подтвердили заказ, ожидайте уведомлений."
    elif action == "order_cancel":
        status = "CANCELLED_BY_PROVIDER"
        message = "Вы отменили заказ."
    elif action == "order_complete":
        status = "COMPLETED"
        message = "Вы выполнили заказ."
    else:
        status = "UNKNOWN"
        message = "Произошла ошибка при обработке статуса заказа"

    url = f"v1/orders/{order_id}/status?status={status}"
    response = await send_request_to_url(url)

    if response["success"]:
        await telegram_bot.send_message(callback_query.message.chat.id, message)
    else:
        error_message = "Не удалось выполнить действие. Попробуйте позже"
        await telegram_bot.send_message(callback_query.message.chat.id, error_message)

    await callback_query.answer(
        message if response["success"] else "Действие не выполнено."
    )


async def send_request_to_url(url, params=None):
    """Отправка HTTP-запроса на внешний URL."""
    try:
        external_url = urljoin(external_api_url, url)
        if params:
            query_string = urlencode(params)
            external_url = f"{external_url}?{query_string}"
        async with aiohttp.ClientSession() as session:
            async with session.put(external_url) as response:
                if response.status == 200:
                    return {"success": True, "message": "Request successful"}
                else:
                    return {
                        "success": False,
                        "message": f"Failed to send request. Status: {response.status}",
                    }
    except Exception as e:
        return {"success": False, "message": f"Error sending request: {e}"}
