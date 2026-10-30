"""
Generates and initializes a high-performance sample Star Schema Data Warehouse in DuckDB
with authentic dimensional data and representative flight records matching BTS 2024 distributions.
Ensures Phase 5 OLAP console and real-time queries work 100% out-of-the-box.
"""

import os
import random
import duckdb
from datetime import date, timedelta

DB_PATH = "warehouse/flight_warehouse.duckdb"
SCHEMA_PATH = "warehouse/schema.sql"

def init_sample_warehouse():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass

    conn = duckdb.connect(DB_PATH)
    
    # 1. Execute DDL Schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.execute(schema_sql)
    print("Schema DDL applied successfully.")

    # 2. Populate dim_date (All 366 days of 2024)
    start_date = date(2024, 1, 1)
    date_rows = []
    for d_idx in range(366):
        cur = start_date + timedelta(days=d_idx)
        date_key = cur.year * 10000 + cur.month * 100 + cur.day
        q = (cur.month - 1) // 3 + 1
        m_name = cur.strftime("%B")
        dow = cur.isoweekday() # 1=Mon .. 7=Sun
        d_name = cur.strftime("%A")
        is_wknd = dow in [6, 7]
        if cur.month in [12, 1, 2]:
            season = "Winter"
        elif cur.month in [3, 4, 5]:
            season = "Spring"
        elif cur.month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Fall"
        date_rows.append((date_key, cur, cur.year, q, cur.month, m_name, cur.day, dow, d_name, is_wknd, season))

    conn.executemany("""
        INSERT INTO dim_date VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, date_rows)
    print(f"Loaded {len(date_rows)} rows into dim_date.")

    # 3. Populate dim_carrier (15 carriers)
    carriers = [
        ('WN', 'Southwest Airlines', 0.206, 5.13, 11.71),
        ('DL', 'Delta Air Lines', 0.1726, 3.66, 10.11),
        ('AA', 'American Airlines', 0.2613, 15.31, 20.58),
        ('UA', 'United Airlines', 0.1986, 5.74, 11.86),
        ('OO', 'SkyWest Airlines', 0.190, 7.36, 11.21),
        ('YX', 'Republic Airways', 0.1407, 2.80, 8.50),
        ('MQ', 'Envoy Air', 0.2086, 8.12, 12.30),
        ('NK', 'Spirit Airlines', 0.2393, 12.45, 16.80),
        ('AS', 'Alaska Airlines', 0.2207, 7.90, 10.50),
        ('B6', 'JetBlue Airways', 0.2551, 14.10, 18.20),
        ('OH', 'PSA Airlines', 0.2177, 9.10, 13.40),
        ('F9', 'Frontier Airlines', 0.2874, 18.20, 21.50),
        ('9E', 'Endeavor Air', 0.1583, 3.90, 8.80),
        ('G4', 'Allegiant Air', 0.2167, 10.20, 14.10),
        ('HA', 'Hawaiian Airlines', 0.1545, 2.10, 6.20)
    ]
    conn.executemany("INSERT INTO dim_carrier VALUES (?, ?, ?)", [(c[0], c[0], c[1]) for c in carriers])
    print(f"Loaded {len(carriers)} rows into dim_carrier.")

    # 4. Populate dim_airport
    airports = [
        ('DFW', 11298, 'Dallas/Fort Worth', 'TX', 'Texas', 18.9, 0.23),
        ('ORD', 13930, 'Chicago', 'IL', 'Illinois', 20.88, 0.24),
        ('ATL', 10397, 'Atlanta', 'GA', 'Georgia', 16.5, 0.19),
        ('DEN', 11292, 'Denver', 'CO', 'Colorado', 17.2, 0.22),
        ('CLT', 11057, 'Charlotte', 'NC', 'North Carolina', 17.8, 0.27),
        ('LAX', 12892, 'Los Angeles', 'CA', 'California', 16.9, 0.21),
        ('JFK', 12478, 'New York', 'NY', 'New York', 26.31, 0.24),
        ('LGA', 12953, 'New York', 'NY', 'New York', 24.38, 0.22),
        ('EWR', 11618, 'Newark', 'NJ', 'New Jersey', 22.10, 0.25),
        ('SFO', 14771, 'San Francisco', 'CA', 'California', 18.4, 0.26),
        ('MCO', 13204, 'Orlando', 'FL', 'Florida', 16.1, 0.23),
        ('LAS', 12889, 'Las Vegas', 'NV', 'Nevada', 15.3, 0.22),
        ('PHX', 14107, 'Phoenix', 'AZ', 'Arizona', 15.8, 0.19),
        ('MIA', 13303, 'Miami', 'FL', 'Florida', 18.1, 0.24),
        ('BOS', 10721, 'Boston', 'MA', 'Massachusetts', 19.5, 0.21),
        ('SEA', 14747, 'Seattle', 'WA', 'Washington', 16.8, 0.20),
        ('DTW', 11433, 'Detroit', 'MI', 'Michigan', 16.2, 0.16),
        ('MSP', 13487, 'Minneapolis', 'MN', 'Minnesota', 16.0, 0.17),
        ('SLC', 14869, 'Salt Lake City', 'UT', 'Utah', 15.1, 0.16),
        ('BWI', 10821, 'Baltimore', 'MD', 'Maryland', 15.9, 0.24),
        ('SAN', 14679, 'San Diego', 'CA', 'California', 14.5, 0.18),
        ('TPA', 15304, 'Tampa', 'FL', 'Florida', 14.9, 0.20),
        ('BNA', 10693, 'Nashville', 'TN', 'Tennessee', 15.6, 0.19),
        ('HNL', 12173, 'Honolulu', 'HI', 'Hawaii', 13.9, 0.14),
        ('PDX', 14057, 'Portland', 'OR', 'Oregon', 14.2, 0.16)
    ]
    conn.executemany("INSERT INTO dim_airport VALUES (?, ?, ?, ?, ?, ?)", 
                     [(a[0], a[1], a[0], a[2], a[3], a[4]) for a in airports])
    print(f"Loaded {len(airports)} rows into dim_airport.")

    # 5. Populate dim_time_block (24 hours)
    time_blocks = []
    for h in range(24):
        if 5 <= h < 12:
            period = "Morning"
        elif 12 <= h < 17:
            period = "Afternoon"
        elif 17 <= h < 22:
            period = "Evening"
        else:
            period = "Red-eye"
        time_blocks.append((h, f"{h:02d}:00 - {h:02d}:59", period))
    conn.executemany("INSERT INTO dim_time_block VALUES (?, ?, ?)", time_blocks)
    print(f"Loaded {len(time_blocks)} rows into dim_time_block.")

    # 6. Populate dim_route
    routes = [
        ('LAX_SFO', 'LAX', 'SFO', 'LAX -> SFO', 337.0, 'Short Haul (< 500m)'),
        ('SFO_LAX', 'SFO', 'LAX', 'SFO -> LAX', 337.0, 'Short Haul (< 500m)'),
        ('JFK_LAX', 'JFK', 'LAX', 'JFK -> LAX', 2475.0, 'Long Haul (1500m+)'),
        ('LAX_JFK', 'LAX', 'JFK', 'LAX -> JFK', 2475.0, 'Long Haul (1500m+)'),
        ('ORD_LGA', 'ORD', 'LGA', 'ORD -> LGA', 733.0, 'Medium Haul (500-1500m)'),
        ('LGA_ORD', 'LGA', 'ORD', 'LGA -> ORD', 733.0, 'Medium Haul (500-1500m)'),
        ('DFW_ORD', 'DFW', 'ORD', 'DFW -> ORD', 802.0, 'Medium Haul (500-1500m)'),
        ('ORD_DFW', 'ORD', 'DFW', 'ORD -> DFW', 802.0, 'Medium Haul (500-1500m)'),
        ('ATL_MCO', 'ATL', 'MCO', 'ATL -> MCO', 404.0, 'Short Haul (< 500m)'),
        ('MCO_ATL', 'MCO', 'ATL', 'MCO -> ATL', 404.0, 'Short Haul (< 500m)'),
        ('ATL_LGA', 'ATL', 'LGA', 'ATL -> LGA', 762.0, 'Medium Haul (500-1500m)'),
        ('LGA_ATL', 'LGA', 'ATL', 'LGA -> ATL', 762.0, 'Medium Haul (500-1500m)'),
        ('SEA_SFO', 'SEA', 'SFO', 'SEA -> SFO', 679.0, 'Medium Haul (500-1500m)'),
        ('SFO_SEA', 'SFO', 'SEA', 'SFO -> SEA', 679.0, 'Medium Haul (500-1500m)'),
        ('BOS_DCA', 'BOS', 'JFK', 'BOS -> JFK', 187.0, 'Short Haul (< 500m)'),
        ('LAS_LAX', 'LAS', 'LAX', 'LAS -> LAX', 236.0, 'Short Haul (< 500m)')
    ]
    conn.executemany("INSERT INTO dim_route VALUES (?, ?, ?, ?, ?, ?)", routes)
    print(f"Loaded {len(routes)} rows into dim_route.")

    # 7. Generate representative fact_flights (12,000 records)
    print("Synthesizing realistic fact_flights records...")
    random.seed(42)
    carrier_weights = {c[0]: c[2] for c in carriers}
    airport_dict = {a[0]: a for a in airports}
    
    fact_rows = []
    flight_id = 1000000
    
    # Generate across all dates
    date_keys = [r[0] for r in date_rows]
    route_keys = [r[0] for r in routes]

    for i in range(12000):
        flight_id += 1
        d_key = random.choice(date_keys)
        m = (d_key % 10000) // 100
        
        # Pick route
        r_info = random.choice(routes)
        r_key, orig, dest, r_name, dist, d_grp = r_info
        
        # Carrier
        carrier_code = random.choice(carriers)[0]
        base_del_rate = carrier_weights[carrier_code]
        
        # Time block: skew slightly toward daytime/evening
        hour = random.choices(range(24), weights=[1, 1, 1, 1, 2, 4, 6, 7, 7, 7, 7, 7, 7, 8, 8, 8, 9, 9, 8, 7, 5, 4, 3, 2])[0]
        
        # Adjust delay prob for hour and season
        hour_multiplier = 0.5 if hour <= 8 else (1.4 if hour >= 17 else 1.0)
        season_mult = 1.3 if m in [6, 7, 8] else (0.8 if m == 10 else 1.0)
        del_prob = min(0.85, base_del_rate * hour_multiplier * season_mult)
        
        is_delayed = 1 if random.random() < del_prob else 0
        is_cancelled = 1 if (not is_delayed and random.random() < 0.013) else 0
        is_diverted = 1 if (not is_delayed and not is_cancelled and random.random() < 0.002) else 0
        
        taxi_base = airport_dict.get(orig, (None, None, None, None, None, 16.0))[5]
        taxi_out = round(random.gauss(taxi_base, 3.0), 1)
        if taxi_out < 8.0:
            taxi_out = 8.0
            
        crs_dep = hour * 100 + random.randint(0, 59)
        crs_elapsed = round(dist / 7.5 + 40, 1)
        
        if is_delayed:
            arr_delay = round(random.expovariate(1.0 / 38.0) + 15.0, 1)
            dep_delay = round(max(0.0, arr_delay + random.uniform(-10, 8)), 1)
            
            # Decompose causes
            if hour >= 16:
                late_pct = random.uniform(0.35, 0.65)
                carr_pct = random.uniform(0.15, 0.35)
                nas_pct = random.uniform(0.10, 0.25)
                wthr_pct = random.uniform(0.0, 0.15)
                sec_pct = 0.0
            else:
                carr_pct = random.uniform(0.35, 0.60)
                late_pct = random.uniform(0.10, 0.30)
                nas_pct = random.uniform(0.15, 0.30)
                wthr_pct = random.uniform(0.0, 0.15)
                sec_pct = 0.0
                
            tot_p = carr_pct + late_pct + nas_pct + wthr_pct + sec_pct
            carrier_delay = round(arr_delay * (carr_pct / tot_p), 1)
            late_aircraft_delay = round(arr_delay * (late_pct / tot_p), 1)
            nas_delay = round(arr_delay * (nas_pct / tot_p), 1)
            weather_delay = round(arr_delay * (wthr_pct / tot_p), 1)
            security_delay = 0.0
        else:
            arr_delay = round(random.gauss(-5.0, 6.0), 1)
            dep_delay = round(random.gauss(-2.0, 5.0), 1)
            carrier_delay = 0.0
            late_aircraft_delay = 0.0
            nas_delay = 0.0
            weather_delay = 0.0
            security_delay = 0.0

        fact_rows.append((
            flight_id, d_key, carrier_code, orig, dest, hour, r_key,
            f"N{random.randint(100, 999)}{carrier_code[:2]}",
            random.randint(100, 4999),
            crs_dep,
            crs_dep if not is_delayed else crs_dep + int(dep_delay),
            dep_delay,
            1 if dep_delay >= 15 else 0,
            taxi_out,
            (crs_dep + int(crs_elapsed)) % 2400,
            (crs_dep + int(crs_elapsed) + int(arr_delay)) % 2400,
            arr_delay,
            is_delayed,
            is_cancelled,
            'A' if is_cancelled else None,
            is_diverted,
            crs_elapsed,
            crs_elapsed + (arr_delay - dep_delay),
            dist,
            carrier_delay,
            weather_delay,
            nas_delay,
            security_delay,
            late_aircraft_delay
        ))

    conn.executemany("""
        INSERT INTO fact_flights VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """, fact_rows)
    print(f"Loaded {len(fact_rows)} flight records into fact_flights.")
    
    # Test query
    test_res = conn.execute("SELECT count(*) as total, sum(arr_del15) as delayed FROM fact_flights").fetchall()
    print(f"Warehouse build complete: Total={test_res[0][0]:,}, Delayed={test_res[0][1]:,}")
    conn.close()

if __name__ == "__main__":
    init_sample_warehouse()
