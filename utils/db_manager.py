import os
import sqlite3
import json
from typing import List, Dict, Any, Tuple

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "trips.db")

def init_db():
    """Initializes the database directory and tables if they don't already exist."""
    # Ensure database folder exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create trips table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            days INTEGER NOT NULL,
            budget REAL NOT NULL,
            preferences TEXT,
            itinerary_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def save_trip(destination: str, days: int, budget: float, preferences: List[str], itinerary_data: Dict[str, Any]) -> int:
    """
    Saves a generated trip itinerary into the SQLite database.
    Returns the ID of the newly inserted row.
    """
    init_db()  # Make sure DB is ready
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    prefs_str = ",".join(preferences) if isinstance(preferences, list) else str(preferences)
    itinerary_str = json.dumps(itinerary_data)
    
    cursor.execute("""
        INSERT INTO trips (destination, days, budget, preferences, itinerary_json)
        VALUES (?, ?, ?, ?, ?)
    """, (destination, days, budget, prefs_str, itinerary_str))
    
    trip_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trip_id

def get_all_trips() -> List[Dict[str, Any]]:
    """Retrieves all saved trips, ordered by most recently created."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    # Configure row_factory to get dict-like rows
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM trips ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    trips = []
    for row in rows:
        try:
            itinerary_data = json.loads(row["itinerary_json"])
        except Exception:
            itinerary_data = {}
            
        trips.append({
            "id": row["id"],
            "destination": row["destination"],
            "days": row["days"],
            "budget": row["budget"],
            "preferences": row["preferences"].split(",") if row["preferences"] else [],
            "itinerary_data": itinerary_data,
            "created_at": row["created_at"]
        })
        
    conn.close()
    return trips

def get_trip(trip_id: int) -> Dict[str, Any]:
    """Retrieves a single trip record by ID."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM trips WHERE id = ?", (trip_id,))
    row = cursor.fetchone()
    
    trip = None
    if row:
        try:
            itinerary_data = json.loads(row["itinerary_json"])
        except Exception:
            itinerary_data = {}
            
        trip = {
            "id": row["id"],
            "destination": row["destination"],
            "days": row["days"],
            "budget": row["budget"],
            "preferences": row["preferences"].split(",") if row["preferences"] else [],
            "itinerary_data": itinerary_data,
            "created_at": row["created_at"]
        }
        
    conn.close()
    return trip

def delete_trip(trip_id: int) -> bool:
    """Deletes a trip record by its ID. Returns True if deleted successfully."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

if __name__ == "__main__":
    print("Testing DB Manager...")
    init_db()
    print("DB initialized successfully.")
