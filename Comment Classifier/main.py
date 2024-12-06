import pickle
import voyageai
from dotenv import load_dotenv
import os
from psycopg2.pool import SimpleConnectionPool
import re
import logging
from fastapi import HTTPException

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database configuration
DB_NAME = os.getenv("DB_NAME", "mypostgres")
DB_USER = os.getenv("DB_USER", "mypostgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Initialize database connection pool
pool = SimpleConnectionPool(
    1, 10,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

def get_connection():
    """Get a database connection from the pool."""
    try:
        return pool.getconn()
    except Exception as e:
        logger.error("Database connection error: %s", e)
        raise HTTPException(status_code=500, detail="Database connection error.")

def release_connection(conn):
    """Release a database connection back to the pool."""
    pool.putconn(conn)

# Load VoyageAI API key
api_key = os.getenv("VOYAGEAI_API_KEY")
api_key = "pa-McYB7iT5EsMX96OftXf9-QCiR0NUOSrPEzQPc6wadok"
if not api_key:
    raise ValueError("API key is not found. Please set VOYAGEAI_API_KEY in your .env file.")

# Load the SVM model
model_file = 'svm_classifier_model.pkl'
try:
    with open(model_file, 'rb') as file:
        loaded_model = pickle.load(file)
except Exception as e:
    raise ValueError(f"Failed to load the model: {str(e)}")

try:
    vo = voyageai.Client(api_key=api_key)
except Exception as e:
    raise ValueError(f"Failed to initialize VoyageAI client: {str(e)}")

# Helper functions
def sanitize_comment(comment: str) -> str:
    """Sanitize input to prevent SQL injection."""
    return re.sub(r'[^\w\s]', '', comment).strip()

def get_or_add_comment(comment: str):
    """Check if a comment exists in the database or add it."""
    sanitized_comment = sanitize_comment(comment)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if the comment exists
        select_query = "SELECT id FROM comments WHERE comment = %s;"
        cursor.execute(select_query, (sanitized_comment,))
        result = cursor.fetchone()

        if result:
            return {'id': int(result[0]), 'isNew': False}
        else:
            insert_query = "INSERT INTO comments (comment) VALUES (%s) RETURNING id;"
            cursor.execute(insert_query, (sanitized_comment,))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return {'id': int(new_id), 'isNew': True} 
    except Exception as e:
        logger.error("Database error: %s", e)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            release_connection(conn)


def predict_comment(text: str):
    """Predict the class of a comment."""
    try:
        embedding_response = vo.embed([text], model="voyage-3", input_type="document")
        if not embedding_response.embeddings:
            raise ValueError("Failed to generate embeddings.")

        embedding = embedding_response.embeddings[0]
        prediction = loaded_model.predict([embedding])[0]
        confidence = loaded_model.predict_proba([embedding]).max()

        return {"prediction": int(prediction), "confidence": float(confidence)} 
    except Exception as e:
        logger.error("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
