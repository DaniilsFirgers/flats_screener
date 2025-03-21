import os
import toml
import asyncio
import pytz
from pathlib import Path
from scraper.config import Config, District, ParserConfigs, PpParserConfig, SsParserConfig, City24ParserConfig, TelegramConfig
from scraper.parsers.pp import PardosanasPortalsParser
from scraper.utils.telegram import TelegramBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper.parsers.city_24 import City24Parser
from scraper.utils.logger import logger
from scraper.utils.meta import SingletonMeta
from scraper.parsers.ss import SludinajumuServissParser
from scraper.utils.limiter import RateLimiterQueue
from scraper.database.postgres import postgres_instance


class FlatsParser(metaclass=SingletonMeta):
    def __init__(self):
        self.config = self.load_config()
        self.tg_rate_limiter = RateLimiterQueue(rate=30, per=1, buffer=0.2)
        self.telegram_bot = TelegramBot(self.tg_rate_limiter)
        self.scheduler = AsyncIOScheduler()

    def load_config(self):
        config_path = Path("/app/config.toml")
        with open(config_path, "r", encoding="utf-8") as file:
            data = toml.load(file)

        telegram = TelegramConfig(**data["telegram"])

        parsers_data = data["parsers"]
        parsers = ParserConfigs(
            ss=SsParserConfig(**parsers_data["ss"]),
            city24=City24ParserConfig(**parsers_data["city24"]),
            pp=PpParserConfig(**parsers_data["pp"])
        )

        districts = [District(**district) for district in data["districts"]]

        return Config(telegram=telegram, parsers=parsers, districts=districts, version=data["version"], name=data["name"])

    async def run(self):
        self.tg_rate_limiter.start()
        asyncio.create_task(self.telegram_bot.start_polling())
        await postgres_instance.init_db()

        self.scheduler.configure(timezone=pytz.timezone("Europe/Riga"))

        admin_tg_id = os.getenv("ADMIN_TELEGRAM_ID")
        if admin_tg_id is not None:
            await self.telegram_bot.send_text_msg_with_limiter(
                f"Bot with version {self.config.version} started", admin_tg_id)

        ss = SludinajumuServissParser(self.telegram_bot, self.config.districts,
                                      self.config.parsers.ss)

        city24 = City24Parser(
            self.telegram_bot, self.config.districts, self.config.parsers.city24)

        pp = PardosanasPortalsParser(self.telegram_bot, self.config.districts,
                                     self.config.parsers.pp)

        await asyncio.gather(ss.run(), city24.run(), pp.run())

        loop = asyncio.get_running_loop()

        self.scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(
            ss.run(), loop), "cron", hour="9,12,15,18,21", minute=0, name="SS")

        self.scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(
            city24.run(), loop), "cron", hour="9,12,15,18,21", minute=0, name="City24")

        self.scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(
            pp.run(), loop), "cron", hour="9,12,15,18,21", minute=0, name="PP")

        self.scheduler.start()

        for job in self.scheduler.get_jobs():
            logger.info(
                f"Job {job.id} scheduled to run at {job.next_run_time}")

        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

    async def cleanup(self):
        self.scheduler.shutdown()
        await self.telegram_bot.send_text_msg_with_limiter("Performed cleanup")


if __name__ == "__main__":
    scraper = FlatsParser()
    asyncio.run(scraper.run())
