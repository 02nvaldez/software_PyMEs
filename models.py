from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta, timezone

db = SQLAlchemy()

def get_now():
    # Fuerza la hora de Bogotá (UTC-5) independientemente del servidor
    return datetime.now(timezone(timedelta(hours=-5))).replace(tzinfo=None)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, default="MiNegocio")
    document_id = db.Column(db.String(50), nullable=True) # NIT / RUT
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    logo_path = db.Column(db.String(255), nullable=True) # Path to uploaded logo
    primary_color = db.Column(db.String(20), nullable=False, default="#4f46e5")
    secondary_color = db.Column(db.String(20), nullable=False, default="#0f172a")
    subscription_status = db.Column(db.String(20), nullable=False, default='active') # 'active', 'suspended'
    valid_until = db.Column(db.DateTime, nullable=False, default=lambda: datetime.utcnow() + timedelta(days=30))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee') # 'admin' or 'employee'
    permissions = db.Column(db.Text, nullable=True) # Comma-separated like "inventory,billing,cash,appointments"
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    company = db.relationship('Company', backref='users')
    
    @property
    def has_open_register(self):
        from models import CashRegister
        return CashRegister.query.filter_by(user_id=self.id, status='open').first() is not None

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.String(50), unique=True, nullable=False) # Cédula
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_now)

class CashRegister(db.Model):
    __tablename__ = 'cash_registers'
    id = db.Column(db.Integer, primary_key=True)
    opened_at = db.Column(db.DateTime, nullable=False, default=get_now)
    closed_at = db.Column(db.DateTime, nullable=True)
    initial_balance = db.Column(db.Float, nullable=False, default=0.0)
    final_balance = db.Column(db.Float, nullable=True)
    expected_balance = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='open') # open, closed
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # El empleado que abrió la caja
    
    user = db.relationship('User', backref='cash_registers')
    invoices = db.relationship('Invoice', backref='cash_register', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    sale_price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Float, nullable=False, default=0.0) # Cambiado a Float para soportar gramos/unidades decimales
    is_bundle = db.Column(db.Boolean, default=False) # Si es un combo o receta
    track_stock = db.Column(db.Boolean, default=True) # Si el producto maneja inventario o es un servicio
    min_stock = db.Column(db.Float, nullable=False, default=5.0) # Alerta personalizada
    expiry_date = db.Column(db.Date, nullable=True)
    expiry_alert_days = db.Column(db.Integer, nullable=True, default=30) # Días antes para alertar
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    movements = db.relationship('InventoryMovement', backref='product', lazy=True, cascade="all, delete-orphan")
    components = db.relationship('ProductComponent', 
                                 foreign_keys='ProductComponent.parent_product_id',
                                 backref='parent', 
                                 lazy=True, 
                                 cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'purchase_price': self.purchase_price,
            'sale_price': self.sale_price,
            'stock': self.stock,
            'is_bundle': self.is_bundle,
            'track_stock': self.track_stock,
            'min_stock': self.min_stock
        }

class ProductBatch(db.Model):
    __tablename__ = 'product_batches'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=True) # Opcional: Lote 001, Lote 002
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=get_now)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    product = db.relationship('Product', backref=db.backref('batches', lazy=True, cascade="all, delete-orphan"))

class ProductComponent(db.Model):
    __tablename__ = 'product_components'
    id = db.Column(db.Integer, primary_key=True)
    parent_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    component_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1.0) # Cantidad que se descuenta del insumo

    component = db.relationship('Product', foreign_keys=[component_product_id])

class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    movement_type = db.Column(db.String(10), nullable=False) # 'in' or 'out'
    quantity = db.Column(db.Float, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, default=get_now)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    user = db.relationship('User', backref='inventory_movements')

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(20), nullable=True)
    service = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    importance = db.Column(db.String(20), nullable=False, default='medium') # low, medium, high
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_now)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=True)
    cash_register_id = db.Column(db.Integer, db.ForeignKey('cash_registers.id'), nullable=True)
    date = db.Column(db.DateTime, default=get_now)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    tax_rate = db.Column(db.Float, nullable=False, default=19.0) # Default 19%
    tax_amount = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    client = db.relationship('Client', backref='invoices')
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')
