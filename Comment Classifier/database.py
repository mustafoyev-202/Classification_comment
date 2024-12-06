import psycopg2
import pandas as pd
import re  

DB_NAME = "mypostgres"
DB_USER = "mypostgres"
DB_PASSWORD = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

def sanitize_comment(comment):
    return re.sub(r'[^\w\s]', '', comment).strip()

def import_csv_to_database(csv_file_path):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("Connected to the database.")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            comment TEXT UNIQUE,
            status VARCHAR(50),
            created_at TIMESTAMP,
            company_name VARCHAR(255),
            reject_type_display VARCHAR(255),
            reject_reason_display VARCHAR(255),
            auto_moderate_result VARCHAR(255)
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'comments' is ready.")

        data = pd.read_csv(csv_file_path)

        for _, row in data.iterrows():
            sanitized_comment = sanitize_comment(row['comment'])

            insert_query = """
            INSERT INTO comments (comment, status, created_at, company_name, reject_type_display, reject_reason_display, auto_moderate_result)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (comment) DO NOTHING;
            """
            cursor.execute(insert_query, (
                sanitized_comment,
                row['status'],
                row['created_at'],
                row['company_name'],
                row['reject_type_display'],
                row['reject_reason_display'],
                row['auto_moderate_result']
            ))

        conn.commit()
        print("CSV data has been imported successfully.")

    except Exception as e:
        print("Error:", e)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    csv_file_path = "path_to_your_file.csv"
    import_csv_to_database(csv_file_path)
