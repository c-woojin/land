import abc
import requests
from datetime import date
from typing import List, Dict
from fake_useragent import UserAgent

from src.domain.entity.complex import Complex, Pyeong
from src.domain.values import Region, Price, TradeType


class RequestError(Exception):
    pass


class AbstractLandProvider(abc.ABC):
    def __enter__(self):
        self.establish_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()

    @abc.abstractmethod
    def establish_session(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close_session(self):
        raise NotImplementedError

    @abc.abstractmethod
    def list_regions(self, region_no: str) -> List[Region]:
        raise NotImplementedError

    @abc.abstractmethod
    def list_complexes(self, region_no: str) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_complex_detail(self, complex_no: str) -> Complex:
        raise NotImplementedError

    @abc.abstractmethod
    def list_real_prices(self, complex_no: str, pyeong_no: str, trade_type: TradeType) -> List[Dict[date, List[Price]]]:
        raise NotImplementedError


class NaverLandProvider(AbstractLandProvider):
    def __init__(self, base_url: str = None):
        self.session = None
        self.base_url = base_url or "https://new.land.naver.com/api/"

    def establish_session(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-agent': UserAgent().chrome,
            'Referer': 'https://new.land.naver.com/'
        }

    def close_session(self):
        self.session.close()

    def list_regions(self, region_no: str) -> List[Region]:
        params = {
            'cortarNo': region_no,
        }
        response = self.session.get(self.base_url+"regions/list", params=params)
        if not response.ok:
            raise RequestError("list_regions request to Naver failed.", response.text)
        regions = response.json().get('regionList', [])
        return [Region(region_no=region.get('cortarNo'), region_name=region.get('cortarName')) for region in regions]

    def list_complexes(self, region_no: str) -> List[str]:
        params = {
            'cortarNo': region_no,
            'realEstateType': 'APT:ABYG:JGC'
        }
        response = self.session.get(self.base_url+"regions/complexes", params=params)
        if not response.ok:
            raise RequestError("list_complexes request to Naver failed.", response.text)
        complexes = response.json().get('complexList', [])
        return [complex.get('complexNo') for complex in complexes]

    def get_complex_detail(self, complex_no: str) -> Complex:
        response = self.session.get(self.base_url+"complexes/"+complex_no)
        if not response.ok:
            raise RequestError('complex_details request to Naver failed.', response.text)
        pyeongs = response.json().get('complexPyeongDetailList', [])
        for pyeong in pyeongs:
            try:
                int(pyeong.get('roomCnt'))
            except ValueError:
                pyeong['roomCnt'] = 0
            try:
                int(pyeong.get('bathroomCnt'))
            except ValueError:
                pyeong['bathroomCnt'] = 0
        pyeongs = [Pyeong(
            pyeong_no=pyeong.get('pyeongNo'),
            pyeong_name=pyeong.get('pyeongName2'),
            exclusive_area=pyeong.get('exclusiveArea'),
            exclusive_pyeong=pyeong.get('exclusivePyeong'),
            supply_area=pyeong.get('supplyArea'),
            house_hold_count=pyeong.get('householdCountByPyeong'),
            entrance_type=pyeong.get('entranceType'),
            room_count=self.make_safe_int(pyeong.get('roomCnt')),
            bathroom_count=self.make_safe_int(pyeong.get('bathroomCnt')),
            is_restriction=True if pyeong.get('dealRestrictionYearMonthDay') else False,
        ) for pyeong in pyeongs]
        complex = response.json().get('complexDetail')
        return Complex(
            complex_no=complex.get('complexNo'),
            complex_name=complex.get('complexName'),
            address=complex.get('address', '') + complex.get('detailAddress', ''),
            total_dong_count=self.make_safe_int(complex.get('totalDongCount')),
            total_household_count=self.make_safe_int(complex.get('totalHouseholdCount')),
            completion_date=self.make_completion_date(complex.get('useApproveYmd')),
            high_floor=self.make_safe_int(complex.get('highFloor')),
            type_name=complex.get('realEstateTypeName'),
            pyeongs=pyeongs
        )

    def list_real_prices(self, complex_no: str, pyeong_no: str, trade_type: TradeType) -> List[Dict]:
        params = {
            'complexNo': complex_no,
            'year': 5,
            'tradeType': trade_type.value.get('type_code'),
            'areaNo': pyeong_no,
            'type': 'table'
        }
        response = self.session.get(f"{self.base_url}complexes/{complex_no}/prices/real", params=params)
        if not response.ok:
            raise RequestError('real deal prices request to Naver failed.', response.text)

        return [
            {
                'month': date(int(prices.get('tradeBaseYear')), int(prices.get('tradeBaseMonth')), 1),
                'prices': [
                    Price(
                        trade_date=date(
                            int(price.get('tradeYear')), int(price.get('tradeMonth')), int(price.get('tradeDate'))
                        ),
                        price=self.make_safe_int(price.get(trade_type.value.get('price_field_name'))),
                        floor=self.make_safe_int(price.get('floor'))
                    ) for price in prices.get('realPriceList', [])
                ]
            } for prices in response.json().get('realPriceOnMonthList', [])
        ]

    def make_completion_date(self, ymd: str) -> date:
        year = int(ymd[:4])
        month = int(ymd[4:6]) if ymd[4:6] else 1
        day = int(ymd[6:]) if ymd[6:] else 1
        return date(year=year, month=month, day=day)

    def make_safe_int(self, value) -> int:
        try:
            return int(value)
        except ValueError:
            return 0
