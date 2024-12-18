from dataclasses import dataclass
from typing import List, Literal


@dataclass(frozen=True)
class GeneralConfig:
    city_name: str
    deal_type: Literal["buy", "sell", "hand_over"]
    look_back_argument: Literal["today", "today-2", "today-5"]
    message_sleep: int
    records_delete_interval: int
    db_name: str


@dataclass(frozen=True)
class TelegramConfig:
    token: str
    chat_id: str


@dataclass(frozen=True)
class District:
    name: str
    price_per_m2: int  # TODO:  rename to max_price_per_m2
    min_price_per_m2: int
    rooms: int
    min_m2: int
    min_floor: int
    last_floor: bool


@dataclass(frozen=True)
class Config:
    general: GeneralConfig
    telegram: TelegramConfig
    districts:    List[District]
