import os
from sqlalchemy import create_engine, text  # Import text from SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Create the database engine
engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Test the connection
try:
    # Connect to the database and execute a test query
    with engine.connect() as connection:
        # Query the PostGIS version to ensure PostGIS is enabled
        result = connection.execute(text("SELECT PostGIS_Version();"))
        postgis_version = result.fetchone()[0]
        print(f"Connection successful! PostGIS Version: {postgis_version}")
except Exception as e:
    print(f"Error connecting to the database: {e}")
