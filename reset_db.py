import duckdb

DB_PATH = "car_research.duckdb"

def reset():
    con = duckdb.connect(DB_PATH)
    try:
        con.execute("DELETE FROM CarCostResult")
        con.execute("DELETE FROM ResultInfo")
        con.execute("DELETE FROM CarInfo")
        con.commit()
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    reset()