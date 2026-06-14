import duckdb
from cost_calculator import calc_all_costs, calc_min_annual_income

con = duckdb.connect("car_research.duckdb")

# 스키마 생성
with open("schema.sql", "r", encoding="utf-8") as f:
    con.execute(f.read())

# ----------------------------------------------------------------------
# 샘플 차량 데이터 (사용자가 입력했다고 가정)
# ----------------------------------------------------------------------
cars = [
    (1, "BMW 320i lci2", 55000000, "가솔린", 12000, "images/bmw_320i.png"),
    (2, "Hyundai Avante CN7", 22000000, "가솔린", 15000, "images/avante_cn7.png"),
    (3, "Kia EV3", 42000000, "전기", 18000, "images/kia_ev3.png"),
]

for car in cars:
    con.execute(
        "INSERT INTO CarInfo VALUES (?, ?, ?, ?, ?, ?)", car
    )

# ----------------------------------------------------------------------
# 차량별 부대비용 계산 -> CostInfo 데이터 생성 -> ResultInfo / CarCostResult 저장
# ----------------------------------------------------------------------
record_id = 1
result_id = 1

for car_id, car_name, car_price, fuel_type, annual_mileage, _ in cars:
    costs = calc_all_costs(car_price, fuel_type, annual_mileage)
    min_income = calc_min_annual_income(costs["total_monthly_cost"])

    con.execute(
        "INSERT INTO ResultInfo (result_id, min_annual_income) VALUES (?, ?)",
        (result_id, min_income),
    )

    con.execute(
        """
        INSERT INTO CarCostResult
        (record_id, car_id, result_id, registration_fee, insurance_fee,
         car_tax, fuel_cost, maintenance_cost, total_annual_cost, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id,
            car_id,
            result_id,
            costs["registration_fee"],
            costs["insurance_fee"],
            costs["car_tax"],
            costs["fuel_cost"],
            costs["maintenance_cost"],
            costs["total_annual_cost"],
            f"{car_name} 최초 산출",
        ),
    )
    record_id += 1
    result_id += 1

con.commit()

# ----------------------------------------------------------------------
# 1) 단일 테이블 SELECT 확인
# ----------------------------------------------------------------------
print("=== CarInfo ===")
con.sql("SELECT * FROM CarInfo").show()

print("\n=== ResultInfo ===")
con.sql("SELECT * FROM ResultInfo").show()

print("\n=== CarCostResult ===")
con.sql("SELECT * FROM CarCostResult").show()

# ----------------------------------------------------------------------
# 2) 3개 테이블 LEFT JOIN - 차량별 비용/최소소득 통합 조회
# ----------------------------------------------------------------------
print("\n=== 차량 비용 정보 통합 조회 (3-Table LEFT JOIN) ===")
join_query = """
SELECT
    c.car_id,
    c.car_name,
    c.car_price,
    c.fuel_type,
    c.annual_mileage,
    c.image_path,
    cc.registration_fee,
    cc.insurance_fee,
    cc.car_tax,
    cc.fuel_cost,
    cc.maintenance_cost,
    cc.total_annual_cost,
    r.min_annual_income
FROM CarInfo AS c
LEFT JOIN CarCostResult AS cc ON c.car_id = cc.car_id
LEFT JOIN ResultInfo AS r ON cc.result_id = r.result_id
ORDER BY r.min_annual_income ASC
"""
con.sql(join_query).show()

# ----------------------------------------------------------------------
# 3) 차량별 최소소득 비교 (정렬)
# ----------------------------------------------------------------------
print("\n=== 차량별 최소소득 비교 (낮은 순) ===")
compare_query = """
SELECT c.car_name, r.min_annual_income
FROM ResultInfo AS r
LEFT JOIN CarCostResult AS cc ON r.result_id = cc.result_id
LEFT JOIN CarInfo AS c ON cc.car_id = c.car_id
ORDER BY r.min_annual_income ASC
"""
con.sql(compare_query).show()

con.close()
