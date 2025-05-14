import sqlite3
import argparse
from fastmcp import FastMCP

# Initialize the FastMCP server instance with a namespace "sqlite-demo"
mcp = FastMCP('sqlite-demo')

def init():
    """
    Create (if not exists) the SQLite 'people' table in demo.db
    """
    connection = sqlite3.connect('demo.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
            profession TEXT NOT NULL
        )
    ''')
    connection.commit()
    return connection, cursor

@mcp.tool()
def add_data(query:str) -> bool:
    """Add new data to the people table using a SQL INSERT query.

    Args:
        query (str): SQL INSERT query following this format:
            INSERT INTO people (name, age, profession) 
            VALUES ('John Doe', 30, 'Software Engineer')

    Returns:
        bool: True if data was added successfully, False otherwise.
        
    Example:
        >>> query = '''
        ... INSERT INTO people (name, age, profession) 
        ... VALUES ('John Doe', 30, 'Software Engineer')
        ... '''
        >>> add_data(query)
        True
    """
    connection,cursor = init()
    try:
        cursor.execute(query)
        connection.commit()
        return True
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        connection.close()
        
@mcp.tool()
def read_data(query:str = 'SELECT * FROM people') -> list:
    """Read data from the people table using a SQL SELECT query.
    
    Args:
        query (str,optional): SQL SELECT query. Defaults to "SELECT * FROM people".
            Examples:
                - "SELECT * FROM people"
                - "SELECT name, age FROM people WHERE age > 30"
                - "SELECT * FROM people ORDER BY age DESC"
        
    Returns:
        list: List of tuples containing the query results.
              For default query, tuple format is (id, name, age, profession).

    Example:
        >>> # Read all records
        >>> read_data()
        [(1, 'John Doe', 30, 'Software Engineer'), (2, 'Jane Smith', 25, 'Data Scientist')]
    """
    connection,cursor = init()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []
    finally:
        connection.close()

if __name__ == "__main__":
    # Start the server
    print("Starting server...")
    
    # --- DEBUG MODE ---
    # uv run mcp dev server.py
    
    # --- PRODUCTION MODE ---
    # uv run server.py --server_type=sse
    
    parser = argparse.ArgumentParser(description='Start the FastMCP SQLite demo server')
    parser.add_argument(
        '--server_type', '-s', choices=['sse', 'stdio'], default='sse',
        help='Server mode: SSE (default) or STDIO'
    )
    args = parser.parse_args()
    
    init()
    print(f"Starting FastMCP server in {args.server_type.upper()} mode...")
    mcp.run(args.server_type)
