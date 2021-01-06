import pytest
from faker import Faker
from datetime import date

from src.domain.entity.complex import Pyeong, Complex
from src.domain.values import Price

fake = Faker(['ko-KR'])


class TestRepresentatives:
    @pytest.fixture(scope='function')
    def get_conditions(self):
        return [
            lambda p, c: p.trade_date > c.trade_date,
            lambda p, c: p.trade_date == c.trade_date and p.low_trade_price < c.low_trade_price
        ]

    def test_set_representatives_later_pyeong(self, get_conditions, get_complex: Complex):
        test_complex = get_complex()

        pyeong_early = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_later = Pyeong(
            pyeong_no=2,
            pyeong_name="25B",
            trade_date=date(year=2020, month=11, day=1),
            low_trade_price=10000
        )

        test_complex.add_pyeongs([pyeong_early, pyeong_later])
        test_complex.set_representative_pyeongs(get_conditions)

        pyeong_later.is_representative = True
        assert test_complex.list_representative_pyeongs() == [pyeong_later]

    def test_set_representatives_lower_price_pyeong(self, get_conditions, get_complex: Complex):
        test_complex = get_complex()

        pyeong_high_price = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_low_price = Pyeong(
            pyeong_no=2,
            pyeong_name="25B",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=9000
        )

        test_complex.add_pyeongs([pyeong_high_price, pyeong_low_price])
        test_complex.set_representative_pyeongs(get_conditions)

        pyeong_low_price.is_representative = True
        assert test_complex.list_representative_pyeongs() == [pyeong_low_price]

    def test_set_representatives_multi_pyeongs(self, get_conditions, get_complex: Complex):
        test_complex = get_complex()

        pyeong_a_early = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_a_later = Pyeong(
            pyeong_no=2,
            pyeong_name="25B",
            trade_date=date(year=2020, month=11, day=1),
            low_trade_price=10000
        )

        pyeong_b_high = Pyeong(
            pyeong_no=3,
            pyeong_name="30A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_b_low = Pyeong(
            pyeong_no=4,
            pyeong_name="30B",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=9000
        )

        test_complex.add_pyeongs([pyeong_a_early, pyeong_a_later, pyeong_b_high, pyeong_b_low])
        test_complex.set_representative_pyeongs(get_conditions)

        pyeong_a_later.is_representative = True
        pyeong_b_low.is_representative = True
        assert test_complex.list_representative_pyeongs() == [pyeong_a_later, pyeong_b_low]

    def test_set_representatives_change_conditions(self, get_conditions, get_complex: Complex):
        test_complex = get_complex()

        pyeong_high_price = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_low_price = Pyeong(
            pyeong_no=2,
            pyeong_name="25B",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=9000
        )

        test_complex.add_pyeongs([pyeong_high_price, pyeong_low_price])
        test_complex.set_representative_pyeongs(get_conditions)
        new_conditions = [
            lambda p, c: p.trade_date == c.trade_date and p.low_trade_price > c.low_trade_price
        ]
        test_complex.set_representative_pyeongs(new_conditions)

        pyeong_high_price.is_representative = True
        assert test_complex.list_representative_pyeongs() == [pyeong_high_price]

    def test_set_representatives_additional_pyeongs(self, get_conditions, get_complex: Complex):
        test_complex = get_complex()

        pyeong_early = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        pyeong_later = Pyeong(
            pyeong_no=2,
            pyeong_name="25B",
            trade_date=date(year=2020, month=11, day=1),
            low_trade_price=10000
        )

        test_complex.add_pyeongs([pyeong_early, pyeong_later])
        test_complex.set_representative_pyeongs(get_conditions)

        new_pyeong = Pyeong(
            pyeong_no=3,
            pyeong_name="25C",
            trade_date=date(year=2020, month=12, day=1),
            low_trade_price=20000
        )
        test_complex.add_pyeongs([new_pyeong])
        test_complex.set_representative_pyeongs(get_conditions)

        new_pyeong.is_representative = True
        assert test_complex.list_representative_pyeongs() == [new_pyeong]


class TestPrices:
    def test_select_low_trade_price(self, get_complex: Complex):
        test_complex = get_complex()
        test_pyeong = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        test_complex.add_pyeongs([test_pyeong])
        low_price = Price(trade_date=fake.date(), price=10000, floor=fake.random_int())
        high_price = Price(trade_date=fake.date(), price=20000, floor=fake.random_int())
        price = test_complex.select_trade_price(pyeong_no=1, prices=[low_price, high_price])
        pyeong = test_complex.get_pyeong(pyeong_no=1)

        assert price == low_price
        assert pyeong.trade_date == low_price.trade_date
        assert pyeong.trade_floor == low_price.floor
        assert pyeong.low_trade_price == low_price.price

    def test_select_trade_price_by_floor(self, get_complex: Complex):
        test_complex = get_complex(high_floor=20)
        test_pyeong = Pyeong(
            pyeong_no=1,
            pyeong_name="25A",
            trade_date=date(year=2020, month=10, day=1),
            low_trade_price=10000
        )
        test_complex.add_pyeongs([test_pyeong])
        low_floor_price = Price(trade_date=fake.date(), price=fake.random_int(), floor=1)
        high_floor_price = Price(trade_date=fake.date(), price=fake.random_int(), floor=test_complex.high_floor)
        middle_floor_price = Price(trade_date=fake.date(), price=fake.random_int(), floor=10)
        price = test_complex.select_trade_price(pyeong_no=1, prices=[low_floor_price, high_floor_price, middle_floor_price])
        pyeong = test_complex.get_pyeong(pyeong_no=1)

        assert price == middle_floor_price
        assert pyeong.trade_date == middle_floor_price.trade_date
        assert pyeong.trade_floor == middle_floor_price.floor
        assert pyeong.low_trade_price == middle_floor_price.price
