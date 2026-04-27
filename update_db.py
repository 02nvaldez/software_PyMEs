import sqlite3

def update_database():
    conn = sqlite3.connect('erp_system.db')
    cursor = conn.cursor()
    
    print("Actualizando base de datos...")
    
    # 1. Agregar columna is_bundle a products si no existe
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN is_bundle BOOLEAN DEFAULT 0")
        print("- Columna 'is_bundle' agregada a 'products'.")
    except sqlite3.OperationalError:
        print("- La columna 'is_bundle' ya existe.")

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN track_stock BOOLEAN DEFAULT 1")
        print("- Columna 'track_stock' agregada a 'products'.")
    except sqlite3.OperationalError:
        print("- La columna 'track_stock' ya existe.")

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN min_stock FLOAT DEFAULT 5.0")
        print("- Columna 'min_stock' agregada a 'products'.")
    except sqlite3.OperationalError:
        print("- La columna 'min_stock' ya existe.")

    try:
        cursor.execute("ALTER TABLE cash_registers ADD COLUMN user_id INTEGER REFERENCES users(id)")
        print("- Columna 'user_id' añadida a 'cash_registers'.")
    except sqlite3.OperationalError:
        print("- La columna 'user_id' en 'cash_registers' ya existe.")

    try:
        cursor.execute("ALTER TABLE appointments ADD COLUMN importance VARCHAR(20) DEFAULT 'medium'")
        print("- Columna 'importance' agregada a 'appointments'.")
    except sqlite3.OperationalError:
        print("- La columna 'importance' ya existe.")

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN expiry_date DATE")
        print("- Columna 'expiry_date' agregada a 'products'.")
    except sqlite3.OperationalError:
        print("- La columna 'expiry_date' ya existe.")

    try:
        cursor.execute("ALTER TABLE products ADD COLUMN expiry_alert_days INTEGER DEFAULT 30")
        print("- Columna 'expiry_alert_days' agregada a 'products'.")
    except sqlite3.OperationalError:
        print("- La columna 'expiry_alert_days' ya existe.")

    # 2. Cambiar tipo de dato de stock a FLOAT si es necesario
    # SQLite no permite cambiar el tipo de columna fácilmente, pero permite insertar floats en columnas int
    # No haremos nada aquí por ahora ya que SQLite es flexible.

    # 3. Crear tabla product_components
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_product_id INTEGER NOT NULL,
            component_product_id INTEGER NOT NULL,
            quantity FLOAT NOT NULL DEFAULT 1.0,
            FOREIGN KEY (parent_product_id) REFERENCES products (id),
            FOREIGN KEY (component_product_id) REFERENCES products (id)
        )
    ''')
    print("- Tabla 'product_components' verificada/creada.")

    # 4. Crear tabla product_batches
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_batches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            batch_number VARCHAR(50),
            quantity FLOAT NOT NULL DEFAULT 0.0,
            expiry_date DATE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            company_id INTEGER NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (company_id) REFERENCES company (id)
        )
    ''')
    print("- Tabla 'product_batches' verificada/creada.")

    conn.commit()
    conn.close()
    print("¡Base de datos actualizada!")

if __name__ == "__main__":
    update_database()
