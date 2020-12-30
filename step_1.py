import requests
import csv
import re
from math import floor
from time import sleep
from datetime import datetime, timezone, timedelta
from typing import List
from dataclasses import dataclass
from fake_useragent import UserAgent

REGION_LIST_URL = "https://new.land.naver.com/api/regions/list"
COMPLEX_LIST_URL = "https://new.land.naver.com/api/regions/complexes"
COMPLEX_DETAIL_URL = "https://new.land.naver.com/api/complexes/"


class RequestError(Exception):
    pass


@dataclass
class PyeongDetails:
    exclusive_area: str
    exclusive_pyeong: str
    supply_area: str
    pyeong_name: str
    house_hold_count: int
    entrance_type: str
    room_count: int
    bathroom_count: int
    low_trade_price: int
    trade_date: datetime
    trade_floor: int
    high_lease_price: int
    lease_date: datetime
    lease_floor: int
    is_restriction: bool
    is_representative: bool

    @property
    def formatting_entrance_type(self):
        if self.entrance_type == "계단식":
            return "계"
        elif self.entrance_type == "복도식":
            return "복"
        elif self.entrance_type == '복합식':
            return "합"


@dataclass(frozen=True)
class ComplexDetails:
    complex_name: str
    address: str  # address + detailAddress
    total_dong_count: int
    total_household_count: int
    completion_month: datetime
    pyeongs: List[PyeongDetails]

    def make_rows(self):
        rows = []
        for p in self.pyeongs:
            etc = ""
            int_pyeong = int(re.sub(r'[a-zA-Z]', '', p.pyeong_name))

            if p.trade_date and p.trade_date < datetime.today() - timedelta(days=365):
                etc += f"최근 1년 내 매매거래 없었음."
            elif p.trade_date is None:
                etc += f"매매거래 없음."
            if p.lease_date and p.lease_date < datetime.today() - timedelta(days=365):
                etc += "\n" if len(etc) > 0 else etc
                etc += f"최근 1년 내 전세거래 없었음."
            elif p.lease_date is None:
                etc += "\n" if len(etc) > 0 else etc
                etc += f"전세거래 없음."
            if (p.trade_date is None and p.lease_date is None) and p.is_restriction:
                etc += "\n" if len(etc) > 0 else etc
                etc += f"전매제한"

            rows.append(
                [self.complex_name, f"'{self.completion_month.strftime('%Y-%m')}", self.total_household_count] +
                [p.supply_area, int_pyeong, p.exclusive_area, p.exclusive_pyeong, p.house_hold_count] +
                [p.low_trade_price if p.low_trade_price else "",
                 p.trade_floor if p.trade_floor else "",
                 p.high_lease_price if p.high_lease_price else "",
                 p.lease_floor if p.lease_floor else ""] +
                [p.low_trade_price - p.high_lease_price if p.low_trade_price and p.high_lease_price else '',
                 str(floor(p.high_lease_price/p.low_trade_price*100)) + '%' if p.low_trade_price and p.high_lease_price else '',
                 '@' + str(round(p.low_trade_price/int_pyeong)) if p.low_trade_price else 0,
                 '@' + str(round(p.high_lease_price/int_pyeong)) if p.high_lease_price else 0] +
                [p.room_count, p.bathroom_count, p.formatting_entrance_type, p.pyeong_name, etc] +
                [(p.trade_date.strftime("매매 : %y/%m\n") if p.trade_date else "") + (p.lease_date.strftime("전세 : %y/%m") if p.lease_date else "")] +
                ["v" if p.is_representative else ""]
            )
        return rows


def get_session():
    s = requests.Session()
    s.headers = {
        'User-agent': UserAgent().chrome,
        'Referer': 'https://new.land.naver.com/'
    }
    return s


def get_region_list(cortar_no):
    s = get_session()
    payload = {'cortarNo': str(cortar_no)}
    r = s.get(REGION_LIST_URL, params=payload)
    s.close()
    if not r.ok:
        raise RequestError('Get Complex list request failed.', r.text)
    data = r.json()
    regions = dict()
    count = 1
    for d in data['regionList']:
        regions[count] = [d['cortarName'], d['cortarNo']]
        count += 1
    return regions


def get_complex_list(cortar_no):
    s = get_session()
    payload = {'cortarNo': str(cortar_no), 'realEstateType': 'APT:ABYG:JGC'}
    r = s.get(COMPLEX_LIST_URL, params=payload)
    s.close()
    if not r.ok:
        raise RequestError('Get Complex list request failed.', r.text)

    data = r.json()
    complexes = []

    for d in data['complexList']:
        complexes.append(d['complexNo'])
    return complexes


def get_low_trade_price(prices_by_month, high_floor):
    price, date, floor = None, None, None
    for price_list in prices_by_month:
        real_price_list = price_list['realPriceList']
        candidate_prices = [price for price in real_price_list if int(price['floor']) not in (1, 2, 3, int(high_floor))]

        if candidate_prices:
            low_real_price = min(candidate_prices, key=lambda x: x['dealPrice'])
        elif len(candidate_prices) != len(real_price_list) :
            low_real_price = min(real_price_list, key=lambda x: x['dealPrice'])
        else:
            continue

        price = low_real_price['dealPrice']
        date = datetime(
            int(low_real_price['tradeYear']),
            int(low_real_price['tradeMonth']),
            int(low_real_price['tradeDate'])
        )
        floor = low_real_price['floor']
        break

    return price, date, floor


def get_high_lease_price(prices_by_month, high_floor):
    price, date, floor = None, None, None

    for price_list in prices_by_month:
        real_price_list = price_list['realPriceList']
        candidate_prices = [price for price in real_price_list if int(price['floor']) not in (1, 2, 3, int(high_floor))]

        if candidate_prices:
            low_real_price = max(candidate_prices, key=lambda x: x['leasePrice'])
        elif len(candidate_prices) != len(real_price_list):
            low_real_price = max(real_price_list, key=lambda x: x['leasePrice'])
        else:
            continue

        price = low_real_price['leasePrice']
        date = datetime(
            int(low_real_price['tradeYear']),
            int(low_real_price['tradeMonth']),
            int(low_real_price['tradeDate'])
        )
        floor = low_real_price['floor']
        break

    return price, date, floor


def get_complex_detail(complex_no):
    s = get_session()
    r = s.get(COMPLEX_DETAIL_URL + str(complex_no))

    if not r.ok:
        raise RequestError('Get complex detail list request failed.')

    data = r.json()
    pyeong_details = data['complexPyeongDetailList']
    complex_detail = data['complexDetail']

    pyeongs = []
    for pyeong in pyeong_details:
        print('.', end='\r')
        prices_url = COMPLEX_DETAIL_URL + str(complex_no) + "/prices/real"
        payload = {
            'complexNo': str(complex_no),
            'year': 5,
            'tradeType': 'A1',  # 매매
            'areaNo': pyeong['pyeongNo'],
            'type': 'table'
        }
        high_floor = complex_detail['highFloor']
        r = s.get(prices_url, params=payload)
        data = r.json()
        trade_prices_by_month = data['realPriceOnMonthList']
        low_trade_price, trade_date, trade_floor = get_low_trade_price(trade_prices_by_month, high_floor)

        payload['tradeType'] = 'B1'  # 전세
        r = s.get(prices_url, params=payload)
        data = r.json()
        lease_prices_by_month = data['realPriceOnMonthList']
        high_lease_price, lease_date, lease_floor = get_high_lease_price(lease_prices_by_month, high_floor)

        pyeongs.append(PyeongDetails(
            exclusive_area=pyeong['exclusiveArea'],
            exclusive_pyeong=pyeong['exclusivePyeong'],
            supply_area=pyeong['supplyArea'],
            pyeong_name=pyeong['pyeongName2'],
            house_hold_count=int(pyeong['householdCountByPyeong']),
            entrance_type=pyeong['entranceType'],
            room_count=int(pyeong['roomCnt']),
            bathroom_count=int(pyeong['bathroomCnt']),
            low_trade_price=int(low_trade_price) if low_trade_price else None,
            trade_date=trade_date if trade_date else None,
            trade_floor=int(trade_floor) if trade_floor else None,
            high_lease_price=int(high_lease_price) if high_lease_price else None,
            lease_date=lease_date if lease_date else None,
            lease_floor=int(lease_floor) if lease_floor else None,
            is_restriction=True if pyeong.get('dealRestrictionYearMonthDay') else False,
            is_representative=False
        ))
        ymd = complex_detail['useApproveYmd']
    s.close()

    representatives = {}
    for p in pyeongs:
        int_pyeong = int(re.sub(r'[a-zA-Z]', '', p.pyeong_name))
        representatives.setdefault(int_pyeong, []).append(p)

    for key, items in representatives.items():
        if len(items) == 0:
            continue
        elif len(items) == 1:
            items[0].is_representative = True
            continue
        else:
            candidate = None
            for p in items:
                if candidate is None:
                    candidate = p if p.trade_date else None
                elif p.trade_date and p.trade_date > candidate.trade_date:
                    candidate = p
                elif p.trade_date and p.trade_date == candidate.trade_date and p.low_trade_price < candidate.low_trade_price:
                    candidate = p
            if candidate:
                candidate.is_representative = True

    completion_year = int(ymd[:4]) if ymd[:4] else 5555
    completion_month = int(ymd[4:6]) if ymd[4:6] else 1
    return ComplexDetails(
        complex_name=complex_detail['complexName'],
        address=complex_detail['address'] + complex_detail['detailAddress'],
        total_dong_count=int(complex_detail['totalDongCount']),
        total_household_count=int(complex_detail['totalHouseholdCount']),
        completion_month=datetime(completion_year, completion_month, 1),
        pyeongs=pyeongs
    )


def main():
    print("초기화중...\r", end='')
    cities = get_region_list("0000000000")
    print("            \r", end='')
    print("STEP 1")
    for no in cities.keys():
        print(no, cities[no][0])
    while True:
        try:
            i = int(input("데이터를 수집할 도시의 번호를 입력하여 주세요. : "))
            selected_city = cities[i][0]
            cortar_no = cities[i][1]
        except KeyError:
            print("정확한 번호를 입력하세요!")
            continue
        break

    print()
    print("STEP 2", selected_city)
    dvsns = get_region_list(cortar_no)
    for no in dvsns.keys():
        print(no, dvsns[no][0])
    while True:
        try:
            i = int(input("데이터를 수집할 구역의 번호를 입력하여 주세요. : "))
            selected_dvsns = dvsns[i][0]
            cortar_no = dvsns[i][1]
        except KeyError:
            print("정확한 번호를 입력하세요!")
            continue
        break

    print()
    print("STEP 3", selected_city, selected_dvsns)
    towns = get_region_list(cortar_no)
    for no in towns.keys():
        print(no, towns[no][0])
    while True:
        try:
            i = int(input("데이터를 수집할 동네의 번호를 입력하여 주세요. : "))
            selected_towns = towns[i][0]
            cortar_no = towns[i][1]
        except KeyError:
            print("정확한 번호를 입력하세요!")
            continue
        break

    created_time = datetime.now(timezone(timedelta(hours=9)))
    file_name = f"{selected_city}_{selected_dvsns}_{selected_towns}_({created_time.strftime('%y%m%d_%H%M%S')})"
    with open(f'./{file_name}.csv', 'w', encoding='utf-8-sig', newline='') as f:
        wt = csv.writer(f)
        wt.writerow(['단지명', '입주연도', '총세대수', '공급(㎡)', '공급면적', '전용(㎡)', '전용면적', '세대', '매매최저가', '층',
                     '전세최고가', '층', '매전갭', '전세가율', '매매평단', '전세평단', '방', '욕실', '구조', '타입', '비고', '거래일자',
                     '대표평형'])
        print(f'\n{selected_city} {selected_dvsns} {selected_towns} 데이터 수집을 시작합니다...')
        complexes = get_complex_list(cortar_no)
        print(f'{len(complexes)}개 단지 리스트를 수집합니다...')
        count = 1
        for complex_no in complexes:
            sleep(0.5)
            print(f'[{count}/{len(complexes)}] 수집중...', end='\r')
            c = get_complex_detail(complex_no)
            wt.writerows(c.make_rows())
            wt.writerow([""])
            print(f'[{count}/{len(complexes)}] {c.complex_name} 단지 데이터를 수집을 완료하였습니다!')
            count += 1

    print('데이터 수집을 완료하였습니다...')


main()
