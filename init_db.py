from app import app, db
from models import Product, User, Company
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Crear las tablas
        db.create_all()
        
        # Check if company exists
        company = Company.query.first()
        if not company:
            company = Company(
                name='MiNegocio S.A.S.',
                document_id='NIT 123456789-0',
                phone='+1 234 567 890',
                email='contacto@empresa.com',
                address='Calle 123 #45-67, Ciudad'
            )
            db.session.add(company)
            db.session.flush() # Obtenemos el ID de la empresa para el usuario
            
        # Check if admin exists
        admin = User.query.filter_by(email='admin@erp.com').first()
        if not admin:
            hashed_pw = generate_password_hash('admin123')
            admin = User(
                email='admin@erp.com', 
                name='Administrador Principal',
                password_hash=hashed_pw,
                role='admin',
                permissions='all',
                is_active=True,
                must_change_password=False,
                company_id=company.id
            )
            db.session.add(admin)
            
        db.session.commit()
        print("Base de datos inicializada correctamente.")
        print("Usuario Admin: admin@erp.com")
        print("Contraseña Admin: admin123")

if __name__ == '__main__':
    init_db()
