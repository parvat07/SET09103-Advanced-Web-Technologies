from app import app, db
from sqlalchemy import inspect

# Ensure the app context is pushed
with app.app_context():
    # Create all tables
    db.create_all()

    # Use Inspector to get table names
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    print("Tables in the database:", tables)
