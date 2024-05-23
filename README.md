## GDP Data Ingestion Pipeline
### Overview
This project demonstrates a data ingestion pipeline designed to fetch Gross Domestic Product (GDP) data for South American countries from the World Bank API and load it into a PostgreSQL database. The goal is to create a reliable and efficient pipeline using Python and PostgreSQL, adhering to best practices in data engineering.

### Features
Data Extraction: Fetches GDP data for South American countries from the World Bank API.
Data Transformation: Ensures data integrity by handling null values and mapping country codes.
Data Loading: Inserts cleaned and validated data into a PostgreSQL database.
Configuration Management: Utilizes dotenv for managing environment variables securely.


### Database Schema

The data is loaded into a PostgreSQL database with the following schema:

- `country` table:
  - `id` (SERIAL PRIMARY KEY)
  - `name` (VARCHAR(255))
  - `iso3_code` (VARCHAR(3) UNIQUE)

- `gdp` table:
  - `id` (SERIAL PRIMARY KEY)
  - `country_id` (INT REFERENCES country(id))
  - `year` (INT)
  - `value` (FLOAT)

### Query

A SQL query is used to generate a pivoted report of the GDP data for the last five years, rounded to two decimal points and presented in billions of USD.

## Setup Instructions

### Prerequisites

- Python 3.x
- PostgreSQL
- `requests` library
- `psycopg2` library
- `python-dotenv` library

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/south-american-gdp-pipeline.git
    cd south-american-gdp-pipeline
    ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required Python libraries:
    ```sh
    pip install requests psycopg2-binary python-dotenv
    ```

4. Set up the PostgreSQL database:
    - Create a new PostgreSQL database.
    - Run the following SQL commands to create the necessary tables:

    ```sql
    CREATE TABLE country (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        iso3_code VARCHAR(3) UNIQUE
    );

    CREATE TABLE gdp (
        id SERIAL PRIMARY KEY,
        country_id INT REFERENCES country(id),
        year INT,
        value FLOAT
    );
    ```

5. Create a `.env` file in the project directory with your PostgreSQL database credentials:
    ```env
    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=your_database_host
    DB_PORT=your_database_port
    ```

## Usage

### Running the Data Ingestion Script

To run the data ingestion script and load the GDP data into the PostgreSQL database, execute the following command:

```sh
python data_ingestion.py
```


### SQL Query for Pivoted Report

Run the following SQL query to generate a pivoted report of the GDP data for the last five years, rounded to two decimal points and presented in billions of USD:

```sql
SELECT 
    c.id,
    c.name,
    c.iso3_code,
    ROUND(CAST(COALESCE(MAX(CASE WHEN g.year = 2019 THEN g.value END) / 1e9, 0) AS numeric), 2) AS "2019",
    ROUND(CAST(COALESCE(MAX(CASE WHEN g.year = 2020 THEN g.value END) / 1e9, 0) AS numeric), 2) AS "2020",
    ROUND(CAST(COALESCE(MAX(CASE WHEN g.year = 2021 THEN g.value END) / 1e9, 0) AS numeric), 2) AS "2021",
    ROUND(CAST(COALESCE(MAX(CASE WHEN g.year = 2022 THEN g.value END) / 1e9, 0) AS numeric), 2) AS "2022",
    ROUND(CAST(COALESCE(MAX(CASE WHEN g.year = 2023 THEN g.value END) / 1e9, 0) AS numeric), 2) AS "2023"
FROM 
    country c
LEFT JOIN 
    gdp g ON c.id = g.country_id
GROUP BY 
    c.id, c.name, c.iso3_code
ORDER BY 
    c.name;
```

### Assumptions and Design Decisions

- The country table is populated with unique country codes (iso3_code) to avoid duplicate entries.
- The gdp table stores the GDP values, linked to the corresponding country by country_id.
- The data ingestion script handles missing GDP values by skipping entries with None values.
- The pivoted report rounds GDP values to two decimal points and converts them to billions of USD for better readability.

## Conclusion
This project demonstrates a complete data ingestion pipeline from data extraction to database loading and querying. The provided setup and usage instructions should help you replicate the process and generate the desired reports.

