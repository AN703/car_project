"""
차자보기 (Car Affordability Research)
차량 정보를 바탕으로 부대비용과 최소 필요 소득을 계산하는 모듈
"""

# 연료 종류별 1km 당 평균 유류비 (원/km) - 2026년 평균 유가 기준 가정치
FUEL_COST_PER_KM = {
    "가솔린": 180,
    "디젤": 160,
    "LPG": 120,
    "전기": 40,
    "하이브리드": 110,
}

# 소득 대비 차량 유지비 적정 비율 (가정: 연간 소득의 15%를 넘지 않아야 함)
INCOME_RATIO = 0.15


def calc_registration_fee(car_price: int) -> int:
    """등록비용(취득세 등) = 차량 정가의 7% (1회성 비용을 12개월로 환산)"""
    acquisition_tax = car_price * 0.07
    return round(acquisition_tax)


def calc_insurance_fee(car_price: int) -> int:
    """보험료 = 차량 정가의 3% (연간 추정)"""
    return round(car_price * 0.03 / 12)


def calc_car_tax(car_price: int) -> int:
    """자동차세 = 차량 정가의 1.5% (연간 추정)"""
    return round(car_price * 0.015 / 12)


def calc_fuel_cost(fuel_type: str, annual_mileage: int) -> int:
    """유류비 = 연간 주행거리 x 연료별 km당 비용"""
    rate = FUEL_COST_PER_KM.get(fuel_type, 150)
    return round(annual_mileage * rate / 12)


def calc_maintenance_cost(car_price: int) -> int:
    """정비비 = 차량 정가의 1% (연간 추정)"""
    return round(car_price * 0.01 / 12)


def calc_all_costs(car_price: int, fuel_type: str, annual_mileage: int) -> dict:
    """월 기준 부대비용 항목 전체 계산"""
    registration_fee = calc_registration_fee(car_price)
    insurance_fee = calc_insurance_fee(car_price)
    car_tax = calc_car_tax(car_price)
    fuel_cost = calc_fuel_cost(fuel_type, annual_mileage)
    maintenance_cost = calc_maintenance_cost(car_price)

    total_monthly_cost = (
        registration_fee + insurance_fee + car_tax + fuel_cost + maintenance_cost
    )

    return {
        "registration_fee": registration_fee,
        "insurance_fee": insurance_fee,
        "car_tax": car_tax,
        "fuel_cost": fuel_cost,
        "maintenance_cost": maintenance_cost,
        "total_annual_cost": total_monthly_cost * 12,
        "total_monthly_cost": total_monthly_cost,
    }


def calc_min_annual_income(total_monthly_cost: int) -> int:
    """
    최소 필요 연 소득 계산
    월 부대비용이 소득의 INCOME_RATIO(15%)를 넘지 않도록 하는 최소 연 소득
    """
    min_monthly_income = total_monthly_cost / INCOME_RATIO
    return round(min_monthly_income * 12)


if __name__ == "__main__":
    costs = calc_all_costs(55000000, "가솔린", 12000)
    income = calc_min_annual_income(costs["total_monthly_cost"])
    print(costs)
    print("최소 연 소득(만원):", income // 10000)
