import pytest
from faker import Faker

from src.domain.entity.complex import Complex

fake = Faker(['ko_KR'])


@pytest.fixture(scope='function')
def get_complex():
    def _complex(complex_no: str = None, name: str = None, high_floor: int = None):
        return Complex(
            complex_no=complex_no or fake.random_int(),
            complex_name=name or "Test_Complex",
            address=fake.address(),
            total_dong_count=fake.random_int(),
            total_household_count=fake.random_int(),
            completion_date=fake.date(),
            high_floor=high_floor or fake.random_int()
        )

    return _complex
