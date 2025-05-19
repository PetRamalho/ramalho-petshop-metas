#!/usr/bin/env python
import os
import sys
# Adiciona o diretório src ao sys.path para permitir importações relativas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "src"))

from src.main import app, db # Importa app e db de src.main
from src.models.user import User # Importa o modelo User

# Configuração do SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

def create_users():
    with app.app_context():
        db.create_all() # Garante que todas as tabelas existam

        users_data = [
            {"username": "Adm", "password": "adm123", "role": "master", "store_name": None},
            {"username": "alvarenga", "password": "alvarenga123", "role": "loja", "store_name": "Alvarenga"},
            {"username": "corbisier", "password": "corbisier321", "role": "loja", "store_name": "Corbisier"},
            {"username": "piraporinha", "password": "piraporinha321", "role": "loja", "store_name": "Piraporinha"}
        ]

        for user_data in users_data:
            user = User.query.filter_by(username=user_data["username"]).first()
            if not user:
                new_user = User(username=user_data["username"], role=user_data["role"], store_name=user_data["store_name"])
                new_user.set_password(user_data["password"])
                db.session.add(new_user)
                print(f"Usuário {user_data['username']} criado.")
            else:
                print(f"Usuário {user_data['username']} já existe.")
        
        db.session.commit()
        print("Usuários iniciais configurados.")

if __name__ == "__main__":
    create_users()

