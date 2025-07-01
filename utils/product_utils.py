import sqlite3
from config import DB_PATH

def get_all_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, price, image FROM products")
    products = cursor.fetchall()

    conn.close()
    return products
