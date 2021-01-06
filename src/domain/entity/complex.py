import re
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date

from src.domain.values import Price


@dataclass
class Pyeong:
    pyeong_no: str
    pyeong_name: str
    exclusive_area: Optional[str] = None
    exclusive_pyeong: Optional[str] = None
    supply_area: Optional[str] = None
    house_hold_count: Optional[int] = None
    entrance_type: Optional[str] = None
    room_count: Optional[int] = None
    bathroom_count: Optional[int] = None
    low_trade_price: Optional[int] = None
    trade_date: Optional[date] = None
    trade_floor: Optional[int] = None
    high_lease_price: Optional[int] = None
    lease_date: Optional[date] = None
    lease_floor: Optional[int] = None
    is_restriction: Optional[bool] = False
    is_representative: Optional[bool] = False

    @property
    def formatting_entrance_type(self):
        if self.entrance_type == "계단식":
            return "계"
        elif self.entrance_type == "복도식":
            return "복"
        elif self.entrance_type == '복합식':
            return "합"

    @property
    def int_pyeong(self):
        return int(re.sub(r'[a-zA-Z]', '', self.pyeong_name))


@dataclass
class Complex:
    complex_no: str
    complex_name: str
    address: Optional[str] = None  # address + detailAddress
    total_dong_count: Optional[int] = None
    total_household_count: Optional[int] = None
    completion_date: Optional[date] = None
    high_floor: Optional[int] = None
    type_name: Optional[str] = None
    pyeongs: Optional[List[Pyeong]] = field(default_factory=list)

    LOW_FLOOR = [1, 2, 3]

    def get_pyeong(self, pyeong_no: str) -> Pyeong:
        return next(pyeong for pyeong in self.pyeongs if pyeong.pyeong_no == pyeong_no)

    def add_pyeongs(self, pyeongs: List[Pyeong]):
        current_pyeongs = [p.pyeong_name for p in self.pyeongs]
        for p in pyeongs:
            if p.pyeong_name in current_pyeongs :
                continue
            else:
                self.pyeongs.append(p)
        return self.pyeongs

    def list_representative_pyeongs(self):
        return [p for p in self.pyeongs if p.is_representative]

    def set_representative_pyeongs(self, representative_conditions):
        candidates_by_pyeong = {}
        for p in self.pyeongs:
            p.is_representative = False
            int_p = int(re.sub(r'[a-zA-Z]', '', p.pyeong_name))
            if p.trade_date:
                candidate = candidates_by_pyeong.setdefault(int_p, p)
                for condition in representative_conditions:
                    if condition(p, candidate):
                        candidates_by_pyeong[int_p] = p

        for pyeong in candidates_by_pyeong.values():
            pyeong.is_representative = True

        return candidates_by_pyeong.values()

    def select_trade_price(self, pyeong_no: str, prices: List[Price]) -> Price:
        assert len(prices) > 0
        if len(prices) == 1:
            selected_price = prices[0]
        else:
            candidate_prices = [
                price for price in prices if price.floor not in self.LOW_FLOOR + ([self.high_floor] or [])
            ] or prices
            selected_price = min(candidate_prices, key=lambda p: p.price)

        pyeong = self.get_pyeong(pyeong_no)
        pyeong.trade_date = selected_price.trade_date
        pyeong.trade_floor = selected_price.floor
        pyeong.low_trade_price = selected_price.price
        return selected_price

    def select_lease_price(self, pyeong_no: str, prices: List[Price]) -> Price:
        assert len(prices) > 0
        if len(prices) == 1:
            selected_price = prices[0]
        else:
            candidate_prices = [
                price for price in prices if price.floor not in self.LOW_FLOOR + ([self.high_floor] or [])
            ] or prices
            selected_price = max(candidate_prices, key=lambda p: p.price)

        pyeong = self.get_pyeong(pyeong_no)
        pyeong.lease_date = selected_price.trade_date
        pyeong.lease_floor = selected_price.floor
        pyeong.high_lease_price = selected_price.price
        return selected_price
