from db import db  # Importe do seu módulo principal
from models import Servico  # Importe seu modelo
from sqlalchemy import insert  # Para usar a sintaxe mais moderna

# Se precisar de conexão direta (alternativa)
from app import db, app  # Importe sua aplicação Flask

def popular_servicos():
    with app.app_context():  # Cria contexto de aplicação
        try:
            # Sintaxe moderna do SQLAlchemy 2.0
            stmt = insert(Servico).values([
                {'id': 1, 'nome': 'Corte'},
                {'id': 2, 'nome': 'Barba'},
                {'id': 3, 'nome': 'Manicure'},
                {'id': 4, 'nome': 'Pedicure'},
                {'id': 5, 'nome': 'Maquiagem'},
                {'id': 6, 'nome': 'Design de Sobrancelhas'},
                {'id': 7, 'nome': 'Escova'}
            ])
            
            db.session.execute(stmt)
            db.session.commit()
            print("Serviços inseridos com sucesso!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao inserir serviços: {str(e)}")