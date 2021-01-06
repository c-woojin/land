from dataclasses import dataclass
from datetime import date
from enum import Enum


@dataclass(frozen=True)
class Region:
    region_no: int
    region_name: str


@dataclass(frozen=True)
class Price:
    trade_date: date
    price: int
    floor: int


class TradeType(Enum):
    DEAL = {'type_code': 'A1', 'price_field_name': 'dealPrice'}  # 매매
    LEASE = {'type_code': 'B1', 'price_field_name': 'leasePrice'}  # 전세
