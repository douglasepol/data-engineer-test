import os
import requests
import psycopg2
from dotenv import load_dotenv

# Load database credentials from .env file
load_dotenv()
db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def fetch_gdp_data():
    url = "https://api.worldbank.org/v2/country/ARG;BOL;BRA;CHL;COL;ECU;GUY;PRY;PER;SUR;URY;VEN/indicator/NY.GDP.MKTP.CD?format=json&page=1&per_page=50"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[1]  # The data is in the second element of the list
    else:
        response.raise_for_status()

def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def insert_country_data(conn, country_name, iso3_code):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO country (name, iso3_code)
                VALUES (%s, %s)
                ON CONFLICT (iso3_code) DO NOTHING
                RETURNING id
            """, (country_name, iso3_code))
            conn.commit()
            if cursor.rowcount:
                return cursor.fetchone()[0]
            else:
                cursor.execute("SELECT id FROM country WHERE iso3_code = %s", (iso3_code,))
                return cursor.fetchone()[0]
    except psycopg2.Error as e:
        print(f"Error inserting country data: {e}")
        conn.rollback()
        return None

def insert_gdp_data(conn, country_id, year, value):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO gdp (country_id, year, value)
                VALUES (%s, %s, %s)
            """, (country_id, year, value))
            conn.commit()
    except psycopg2.Error as e:
        print(f"Error inserting GDP data: {e}")
        conn.rollback()

def get_country_id_map(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, iso3_code FROM country")
            return {iso3_code: id for id, iso3_code in cursor.fetchall()}
    except psycopg2.Error as e:
        print(f"Error retrieving country ID map: {e}")
        return {}

def main():
    gdp_data = fetch_gdp_data()
    if not gdp_data:
        print("No GDP data fetched")
        return

    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        return

    country_id_map = get_country_id_map(conn)

    for entry in gdp_data:
        country_name = entry['country']['value']
        iso3_code = entry['countryiso3code']
        year = int(entry['date'])
        value = entry['value']

        if value is None:
            continue  # Skip entries with missing GDP values

        if iso3_code not in country_id_map:
            country_id = insert_country_data(conn, country_name, iso3_code)
            if country_id:
                country_id_map[iso3_code] = country_id
            else:
                print(f"Failed to insert country data for {country_name} ({iso3_code})")
                continue
        else:
            country_id = country_id_map[iso3_code]

        insert_gdp_data(conn, country_id, year, value)

    conn.close()

if __name__ == "__main__":
    main()
