"""
차자보기 (Car Affordability Research, CAR)
Flet + DuckDB 기반 GUI 애플리케이션
"""


import os
import flet as ft
import duckdb
from cost_calculator import calc_all_costs, calc_min_annual_income

DB_PATH = "car_research.duckdb"
ASSETS_PATH = "assets"

def get_connection():
    return duckdb.connect(DB_PATH)

def main(page: ft.Page):
    page.title = "차자보기 - Car Affordability Research"
    page.window.width = 1200
    page.window.height = 1300
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = "#F4F6F8"

    history_row = ft.Row(spacing=10, scroll=ft.ScrollMode.AUTO, vertical_alignment=ft.CrossAxisAlignment.START)

    # [추가] 클릭 시 데이터 불러오는 함수
    def load_car_data(car_id):
        con = get_connection()
        data = con.execute("""
            SELECT c.car_name, cc.registration_fee, cc.insurance_fee, cc.car_tax, 
                   cc.fuel_cost, cc.maintenance_cost, r.min_annual_income
            FROM CarInfo c
            JOIN CarCostResult cc ON c.car_id = cc.car_id
            JOIN ResultInfo r ON cc.result_id = r.result_id
            WHERE c.car_id = ?
        """, (car_id,)).fetchone()
        con.close()

        if data:
            name, reg, ins, tax, fuel, maint, min_income = data
            cost_table.controls = [
                ft.Row([ft.Text("등록비용", expand=1), ft.Text(f"{reg:,} 원", expand=1)]),
                ft.Row([ft.Text("보험료", expand=1), ft.Text(f"{ins:,} 원/월", expand=1)]),
                ft.Row([ft.Text("자동차세", expand=1), ft.Text(f"{tax:,} 원/월", expand=1)]),
                ft.Row([ft.Text("유류비", expand=1), ft.Text(f"{fuel:,} 원/월", expand=1)]),
                ft.Row([ft.Text("정비비", expand=1), ft.Text(f"{maint:,} 원/월", expand=1)]),
            ]
            result_text.value = f"{name}의 최소 소득은\n월 {min_income//12//10000:,}만원 이에요!"
            page.update()

    def delete_all(e):
        con = get_connection()
        try:
            con.execute("DELETE FROM CarCostResult")
            con.execute("DELETE FROM ResultInfo")
            con.execute("DELETE FROM CarInfo")
            con.commit()
        except Exception as ex:
            print(f"전체 삭제 중 데이터베이스 오류 발생: {ex}")
        finally:
            con.close()
        refresh_history()

    def refresh_history():
        history_row.controls.clear()
        con = get_connection()
        try:
            rows = con.execute("""
                SELECT c.car_id, c.car_name, c.image_path, r.min_annual_income
                FROM CarInfo c
                LEFT JOIN CarCostResult cc ON c.car_id = cc.car_id
                LEFT JOIN ResultInfo r ON cc.result_id = r.result_id
                ORDER BY c.car_id DESC
            """).fetchall()
        except Exception:
            rows = []
        con.close()

        if not rows:
            history_row.controls.append(ft.Text("검색 내역이 없습니다. 새로운 소득을 계산해보세요!", color="#888888", size=13))
        else:
            for car_id, name, img_path, income in rows:
                local_file_path = ""
                if img_path and img_path.strip():
                    local_file_path = os.path.join(ASSETS_PATH, img_path.strip().lstrip("/"))

                if local_file_path and os.path.exists(local_file_path):
                    thumb = ft.Image(src=img_path.strip(), width=120, height=80, fit=ft.BoxFit.COVER, border_radius=8)
                else:
                    thumb = ft.Container(
                        width=120, height=80, bgcolor="#E0E0E0", border_radius=8,
                        alignment="center", 
                        content=ft.Icon("time_to_leave", size=36, color="#757575"),
                    )

                # [수정] GestureDetector로 감싸 클릭 기능 추가
                history_row.controls.append(
                    ft.GestureDetector(
                        on_tap=lambda e, cid=car_id: load_car_data(cid),
                        content=ft.Container(
                            width=140, padding=10, bgcolor="#FFFFFF", border_radius=10,
                            content=ft.Column([
                                thumb,
                                ft.Text(name, size=13, weight=ft.FontWeight.BOLD, no_wrap=True),
                                ft.Text(f"최소소득 {income//10000:,}만원/년" if income else "계산 필요", size=11, color="#555555"),
                            ], tight=True)
                        )
                    )
                )
        page.update()

    # 입력 폼 필드
    car_name_field = ft.TextField(label="차량 모델명", width=400)
    car_price_field = ft.TextField(label="차량 정가 (원)", width=400, keyboard_type=ft.KeyboardType.NUMBER)
    fuel_type_dropdown = ft.Dropdown(label="차량 연료종류", width=400, options=[
        ft.dropdown.Option("가솔린"), ft.dropdown.Option("디젤"), 
        ft.dropdown.Option("LPG"), ft.dropdown.Option("전기"), ft.dropdown.Option("하이브리드"),
    ])
    mileage_field = ft.TextField(label="연간 예상 주행거리 (km)", width=400, keyboard_type=ft.KeyboardType.NUMBER)
    image_path_field = ft.TextField(label="차량 이미지 경로", width=700, hint_text="images/car.png", helper="assets/images 폴더에 넣은 파일명을 'images/파일명.png' 형식으로 입력")

    result_text = ft.Text("", size=22, weight=ft.FontWeight.BOLD, color="#2E7D32")
    cost_table = ft.Column()

    def on_save_click(e):
        con = get_connection()
        car_id = con.execute("SELECT COALESCE(MAX(car_id),0)+1 FROM CarInfo").fetchone()[0]
        result_id = con.execute("SELECT COALESCE(MAX(result_id),0)+1 FROM ResultInfo").fetchone()[0]
        record_id = con.execute("SELECT COALESCE(MAX(record_id),0)+1 FROM CarCostResult").fetchone()[0]

        car_price = int(car_price_field.value or 0)
        annual_mileage = int(mileage_field.value or 0)
        fuel_type = fuel_type_dropdown.value

        con.execute("INSERT INTO CarInfo VALUES (?, ?, ?, ?, ?, ?)", 
                    (car_id, car_name_field.value, car_price, fuel_type, annual_mileage, image_path_field.value))

        costs = calc_all_costs(car_price, fuel_type, annual_mileage)
        min_income = calc_min_annual_income(costs["total_monthly_cost"])

        con.execute("INSERT INTO ResultInfo (result_id, min_annual_income) VALUES (?, ?)", (result_id, min_income))
        con.execute("""INSERT INTO CarCostResult (record_id, car_id, result_id, registration_fee, insurance_fee,
                        car_tax, fuel_cost, maintenance_cost, total_annual_cost, note)
                        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (record_id, car_id, result_id, costs["registration_fee"], costs["insurance_fee"], 
                     costs["car_tax"], costs["fuel_cost"], costs["maintenance_cost"], costs["total_annual_cost"], 
                     f"{car_name_field.value} 자동 산출"))
        con.commit()
        con.close()

        cost_table.controls = [
            ft.Row([ft.Text("등록비용", expand=1), ft.Text(f"{costs['registration_fee']:,} 원/월", expand=1)]),
            ft.Row([ft.Text("보험료", expand=1), ft.Text(f"{costs['insurance_fee']:,} 원/월", expand=1)]),
            ft.Row([ft.Text("자동차세", expand=1), ft.Text(f"{costs['car_tax']:,} 원/월", expand=1)]),
            ft.Row([ft.Text("유류비", expand=1), ft.Text(f"{costs['fuel_cost']:,} 원/월", expand=1)]),
            ft.Row([ft.Text("정비비", expand=1), ft.Text(f"{costs['maintenance_cost']:,} 원/월", expand=1)]),
        ]
        result_text.value = f"{car_name_field.value}의 최소 소득은\n월 {min_income//12//10000:,}만원 이에요!"
        refresh_history()
        page.update()

    page.add(ft.Column([
        ft.Text("차자보기 (CAR)", size=26, weight=ft.FontWeight.BOLD),
        ft.Row([
            ft.Text("나의 검색내역", size=18, weight=ft.FontWeight.BOLD),
            ft.TextButton("전체 삭제", icon="delete", icon_color="#FF6B6B", on_click=delete_all)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        history_row,
        ft.Divider(),
        ft.Text("소득 계산하기", size=18, weight=ft.FontWeight.BOLD),
        car_name_field, car_price_field, fuel_type_dropdown, mileage_field, image_path_field,
        ft.ElevatedButton("저장하기", on_click=on_save_click, bgcolor="#2E7D32", color="#FFFFFF"),
        ft.Divider(),
        ft.Text("1년 기준 부대비용", size=16, weight=ft.FontWeight.BOLD),
        cost_table,
        result_text,
    ]))
    refresh_history()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")