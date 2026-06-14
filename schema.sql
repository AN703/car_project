-- 차자보기 (Car Affordability Research) DuckDB 스키마
DROP TABLE IF EXISTS CarCostResult;
DROP TABLE IF EXISTS ResultInfo;
DROP TABLE IF EXISTS CarInfo;

-- 차량 기본 정보를 저장하는 테이블 (Entity)
CREATE TABLE CarInfo (
    car_id          INTEGER PRIMARY KEY,
    car_name        VARCHAR NOT NULL,
    car_price       INTEGER NOT NULL,
    fuel_type       VARCHAR NOT NULL,
    annual_mileage  INTEGER NOT NULL,
    image_path      VARCHAR
);

-- 최소 소득 계산 결과를 저장하는 테이블 (Entity)
CREATE TABLE ResultInfo (
    result_id           INTEGER PRIMARY KEY,
    min_annual_income   INTEGER NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CarInfo 와 ResultInfo 를 연결하는 관계 테이블 (Relationship)
-- 한 차량(CarInfo)에 대해 여러 번 비용 산출이 가능 (1:N)
-- 각 산출 기록(CarCostResult)은 하나의 ResultInfo 와 연결 (1:1)
CREATE TABLE CarCostResult (
    record_id           INTEGER PRIMARY KEY,
    car_id              INTEGER NOT NULL,
    result_id           INTEGER NOT NULL,
    registration_fee    INTEGER NOT NULL,
    insurance_fee       INTEGER NOT NULL,
    car_tax             INTEGER NOT NULL,
    fuel_cost           INTEGER NOT NULL,
    maintenance_cost    INTEGER NOT NULL,
    total_annual_cost   INTEGER NOT NULL,
    calc_date           DATE DEFAULT CURRENT_DATE,
    note                VARCHAR,
    FOREIGN KEY (car_id) REFERENCES CarInfo(car_id),
    FOREIGN KEY (result_id) REFERENCES ResultInfo(result_id)
);
