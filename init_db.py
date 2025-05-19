import sqlite3

def init_db():
    """Initialize the database with sample data for testing."""
    connection = sqlite3.connect('demo.db')
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS people(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        profession TEXT NOT NULL
    )
    ''')
    
    # Clear existing data
    cursor.execute("DELETE FROM people")
    
    # Sample data
    sample_data = [
        ('Alice Johnson', 28, 'Data Scientist'),
        ('Bob Smith', 35, 'Software Engineer'),
        ('Carol Davis', 42, 'Product Manager'),
        ('Dave Wilson', 24, 'UX Designer'),
        ('Eva Brown', 31, 'Backend Developer'),
    ]
    
    for person in sample_data:
        cursor.execute(
            "INSERT INTO people (name, age, profession) VALUES (?, ?, ?)",
            person
        )
    
    connection.commit()
    print(f"Database initialized with {len(sample_data)} sample records")
    connection.close()

if __name__ == "__main__":
    init_db()