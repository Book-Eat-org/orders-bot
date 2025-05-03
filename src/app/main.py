from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.routers.book_eat_routers import book_eat_router
from src.app.services.telegram_bot_service import telegram_bot_dispatcher
from src.app.services.telegram_bot_service import telegram_bot


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Запуск бота при старте приложения
    asyncio.create_task(telegram_bot_dispatcher.start_polling(telegram_bot))
    try:
        yield
    finally:
        # остановка бота при старте приложения
        await telegram_bot.session.close()


app = FastAPI(title="TestApi", version="0.2.0", lifespan=lifespan)

app.include_router(book_eat_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)