from app import app, db
from models import Company, User, Product, Client, Invoice, InvoiceItem, CashRegister
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        print("Iniciando inserción de datos de prueba...")
        
        # 1. Crear Empresas
        companies_data = [
            {"name": "TecnoSoluciones S.A.S", "nit": "900.123.456-1"},
            {"name": "Moda Urbana Boutique", "nit": "800.987.654-2"},
            {"name": "Restaurante El Sabor Real", "nit": "700.555.444-3"}
        ]
        
        roles = ['admin', 'employee', 'employee', 'employee', 'employee']
        permissions_list = ["inventory,billing", "billing,cash", "inventory", "appointments", "inventory,billing,cash,appointments"]
        
        for c_info in companies_data:
            # Crear Empresa
            company = Company(
                name=c_info['name'],
                document_id=c_info['nit'],
                address="Calle " + str(random.randint(1, 100)) + " # " + str(random.randint(1, 50)),
                phone="300" + str(random.randint(1000000, 9999999)),
                subscription_status='active',
                valid_until=datetime.utcnow() + timedelta(days=365)
            )
            db.session.add(company)
            db.session.flush() # Para obtener el ID
            
            # 2. Crear Usuarios (5 por empresa)
            domain = c_info['name'].lower().replace(" ", "").replace(".", "")
            for i in range(5):
                role = roles[i]
                user = User(
                    email=f"usuario{i+1}@{domain}.com",
                    name=f"Empleado {i+1} {company.name}",
                    password_hash=generate_password_hash("Password123"),
                    role=role,
                    permissions=permissions_list[i] if role == 'employee' else None,
                    company_id=company.id,
                    must_change_password=False
                )
                db.session.add(user)
            
            # 3. Crear Productos (20 por empresa)
            products = []
            if "Tecno" in company.name:
                items = ["Laptop Pro", "Smartphone X", "Monitor 4K", "Teclado Mecánico", "Mouse Gamer", "Cámara Web", "Disco SSD 1TB", "Memoria RAM 16GB"]
            elif "Moda" in company.name:
                items = ["Camisa Formal", "Jeans Slim", "Chaqueta Cuero", "Vestido Noche", "Zapatos Elegantes", "Gorra Urbana", "Cinturón Piel"]
            else:
                items = ["Hamburguesa Especial", "Pizza Familiar", "Pasta Carbonara", "Ensalada César", "Sopa del Día", "Jugo Natural", "Postre de la Casa"]
                
            for j in range(20):
                base_item = random.choice(items)
                p = Product(
                    name=f"{base_item} Mod. {j+1}",
                    description=f"Descripción detallada del {base_item} para {company.name}",
                    purchase_price=random.randint(10000, 500000),
                    sale_price=random.randint(600000, 1500000) if "Tecno" in company.name else random.randint(20000, 150000),
                    stock=random.randint(5, 50),
                    company_id=company.id
                )
                db.session.add(p)
                products.append(p)
            
            db.session.flush()
            
            # 4. Crear Clientes (10 por empresa)
            clients = []
            for k in range(10):
                cl = Client(
                    document_id=str(random.randint(10000000, 99999999)),
                    name=f"Cliente Frecuente {k+1}",
                    phone="315" + str(random.randint(1000000, 9999999)),
                    company_id=company.id
                )
                db.session.add(cl)
                clients.append(cl)
            
            db.session.flush()
            
            # 5. Crear Caja Registradora
            cash = CashRegister(company_id=company.id, status='open', initial_balance=100000)
            db.session.add(cash)
            db.session.flush()
            
            # 6. Crear Ventas (30 por empresa en los últimos 30 días)
            for m in range(30):
                # Fecha aleatoria en el último mes
                days_ago = random.randint(0, 30)
                invoice_date = datetime.now() - timedelta(days=days_ago)
                
                inv = Invoice(
                    company_id=company.id,
                    client_id=random.choice(clients).id if random.random() > 0.2 else None,
                    cash_register_id=cash.id,
                    date=invoice_date,
                    tax_rate=19.0
                )
                
                # Agregar 1-5 items
                num_items = random.randint(1, 5)
                subtotal = 0
                for _ in range(num_items):
                    prod = random.choice(products)
                    qty = random.randint(1, 3)
                    item_subtotal = prod.sale_price * qty
                    
                    inv_item = InvoiceItem(
                        product_id=prod.id,
                        quantity=qty,
                        unit_price=prod.sale_price,
                        subtotal=item_subtotal
                    )
                    inv.items.append(inv_item)
                    subtotal += item_subtotal
                
                inv.subtotal = subtotal
                inv.tax_amount = subtotal * 0.19
                inv.total = subtotal * 1.19
                db.session.add(inv)
                
        db.session.commit()
        print("¡Datos insertados con éxito!")

if __name__ == "__main__":
    seed_data()
