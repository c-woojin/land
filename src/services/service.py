from typing import List, Dict
from datetime import date

from src.adapters.provider import NaverLandProvider, RequestError, Region
from src.domain.entity.complex import Complex
from src.domain.values import TradeType, Price


def get_main_cities() -> List[Region]:
    provider = NaverLandProvider()
    with provider:
        try:
            cities = provider.list_regions("0000000000")
        except RequestError as e:
            return e
    return cities


def get_regions(region_no: str) -> List[Region]:
    provider = NaverLandProvider()
    with provider:
        try:
            regions = provider.list_regions(region_no)
        except RequestError as e:
            return e
    return regions


def get_complexes(region_no: str) -> List[Complex]:
    provider = NaverLandProvider()
    complexes = []
    with provider:
        try:
            complex_nos = provider.list_complexes(region_no)
            for no in complex_nos:
                c = provider.get_complex_detail(no)
                if '도시형' not in c.complex_name and '오피스텔' not in c.type_name:
                    complexes.append(c)
        except RequestError as e:
            return e
    return complexes


def apply_price(complex: Complex):
    provider = NaverLandProvider()
    with provider:
        try:
            for pyeong in complex.pyeongs:
                trade_prices = provider.list_real_prices(complex.complex_no, pyeong.pyeong_no, TradeType.DEAL)
                trade_prices = trade_prices[0] if trade_prices else []
                if trade_prices and trade_prices.get('prices'):
                    complex.select_trade_price(pyeong.pyeong_no, trade_prices.get('prices'))

                lease_prices = provider.list_real_prices(complex.complex_no, pyeong.pyeong_no, TradeType.LEASE)
                lease_prices = lease_prices[0] if lease_prices else []
                if lease_prices and lease_prices.get('prices'):
                    complex.select_lease_price(pyeong.pyeong_no, lease_prices.get('prices'))

            representatives_condition = [
                lambda p, c: p.trade_date > c.trade_date,
                lambda p, c: p.trade_date == c.trade_date and p.low_trade_price < c.low_trade_price
            ]
            complex.set_representative_pyeongs(representatives_condition)
            complex.set_high_prices()
        except RequestError as e:
            return e
    return complex


def get_prices(complex_no: str, pyeong_no: str, trade_type: TradeType) -> List[Dict[date, List[Price]]]:
    provider = NaverLandProvider()
    with provider:
        try:
            prices = provider.list_real_prices(complex_no=complex_no, pyeong_no=pyeong_no, trade_type=trade_type)
        except RequestError as e:
            return e
    return prices


def find_captain_complex(complexes: List[Complex]) -> Dict[int, Complex]:
    captain_list = dict()
    for c in complexes:
        for p_key, high_price in c.high_prices.items():
            captain = captain_list.setdefault(p_key, c)
            if high_price > captain.high_prices.get(p_key):
                captain_list[p_key] = c
    return captain_list
