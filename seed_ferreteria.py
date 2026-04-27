from app import app, db
from models import Company, User, Product, Client, Invoice, InvoiceItem, CashRegister, ProductComponent
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
import random

def seed_ferreteria():
    with app.app_context():
        print("Insertando datos para Ferretería...")
        
        # 1. Empresa
        company = Company(
            name="Ferretería El Tornillo Maestro",
            document_id="900.555.111-0",
            address="Av. Industrial #45-12",
            phone="3201234567",
            subscription_status='active',
            valid_until=datetime.now(timezone.utc) + timedelta(days=365)
        )
        db.session.add(company)
        db.session.flush()
        
        # 2. Usuarios
        admin = User(
            email="admin@ferreteria.com",
            name="Admin Ferretero",
            password_hash=generate_password_hash("Password123"),
            role='admin',
            company_id=company.id,
            must_change_password=False
        )
        db.session.add(admin)
        
        # 3. Productos (Insumos)
        martillo = Product(name="Martillo de Acero", purchase_price=15000, sale_price=25000, stock=50, company_id=company.id)
        destornillador = Product(name="Destornillador Phillips", purchase_price=5000, sale_price=12000, stock=100, company_id=company.id)
        tacos = Product(name="Tacos 1/4 (Paquete x100)", purchase_price=2000, sale_price=8000, stock=200, company_id=company.id)
        taladro = Product(name="Taladro Percutor 500W", purchase_price=120000, sale_price=185000, stock=15, company_id=company.id)
        cinta = Product(name="Cinta Aislante", purchase_price=1500, sale_price=4500, stock=80, company_id=company.id)
        
        db.session.add_all([martillo, destornillador, tacos, taladro, cinta])
        db.session.flush()
        
        # 4. Combo (Receta)
        kit_hogar = Product(
            name="Kit de Reparación Hogar",
            description="Incluye Martillo, Destornillador y 20 Tacos",
            purchase_price=0, # Se calcula por insumos usualmente
            sale_price=40000,
            stock=0, # El stock es virtual (depende de insumos)
            is_bundle=True,
            company_id=company.id
        )
        db.session.add(kit_hogar)
        db.session.flush()
        
        # Definir componentes del combo
        comp1 = ProductComponent(parent_product_id=kit_hogar.id, component_product_id=martillo.id, quantity=1)
        comp2 = ProductComponent(parent_product_id=kit_hogar.id, component_product_id=destornillador.id, quantity=1)
        comp3 = ProductComponent(parent_product_id=kit_hogar.id, component_product_id=tacos.id, quantity=0.2) # 0.2 paquetes de 100 = 20 tacos
        
        db.session.add_all([comp1, comp2, comp3])
        
        # 5. Algunos clientes y ventas para que se vea lleno
        cl = Client(document_id="10102020", name="Carlos Constructor", company_id=company.id)
        db.session.add(cl)
        db.session.flush()
        
        cash = CashRegister(company_id=company.id, status='open', initial_balance=50000)
        db.session.add(cash)
        db.session.flush()
        
        # Venta del Combo
        inv = Invoice(company_id=company.id, client_id=cl.id, cash_register_id=cash.id, subtotal=40000, tax_amount=7600, total=47600)
        db.session.add(inv)
        db.session.flush()
        
        item = InvoiceItem(invoice_id=inv.id, product_id=kit_hogar.id, quantity=1, unit_price=40000, subtotal=40000)
        db.session.add(item)
        
        # La lógica de descuento de stock se dispararía en el app.py, pero como esto es manual,
        # para que el usuario vea el efecto inmediato en el dashboard, lo haré manual aquí también:
        martillo.stock -= 1
        destornillador.stock -= 1
        tacos.stock -= 0.2
        
        db.session.commit()
        print("¡Ferretería lista! Email: admin@ferreteria.com / Pass: Password123")

if __name__ == "__main__":
    seed_ferreteria()
