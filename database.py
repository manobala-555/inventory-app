import sqlite3
from datetime import datetime


def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create Products table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Product
                   (
                       product_id
                       TEXT
                       PRIMARY
                       KEY,
                       product_name
                       TEXT
                       NOT
                       NULL
                   )
                   ''')

    # Create Location table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Location
                   (
                       location_id
                       TEXT
                       PRIMARY
                       KEY,
                       location_name
                       TEXT
                       NOT
                       NULL
                   )
                   ''')

    # Create ProductMovement table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS ProductMovement
                   (
                       movement_id
                       TEXT
                       PRIMARY
                       KEY,
                       timestamp
                       TEXT
                       NOT
                       NULL,
                       from_location
                       TEXT,
                       to_location
                       TEXT,
                       product_id
                       TEXT
                       NOT
                       NULL,
                       qty
                       INTEGER
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       from_location
                   ) REFERENCES Location
                   (
                       location_id
                   ),
                       FOREIGN KEY
                   (
                       to_location
                   ) REFERENCES Location
                   (
                       location_id
                   ),
                       FOREIGN KEY
                   (
                       product_id
                   ) REFERENCES Product
                   (
                       product_id
                   )
                       )
                   ''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn