import os
from flask import Flask
from flask_login import LoginManager
from src.models.user import db, User

def create_app():
    app = Flask(__name__)
    
    # Configuração do banco de dados
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ramalho_petshop.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração da chave secreta
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-padrao')
    
    # Inicializar extensões
    db.init_app(app)
    
    # Criar tabelas ao iniciar o aplicativo
    with app.app_context():
        db.create_all()
        
        # Verificar se já existem usuários
        if User.query.count() == 0:
            # Criar usuário master
            master = User(
                username="adm",
                role="master",
                store_name="Ramalho Pet Shop"
            )
            master.set_password("adm123")
            
            # Criar usuários de loja
            alvarenga = User(
                username="alvarenga",
                role="loja",
                store_name="Alvarenga"
            )
            alvarenga.set_password("alvarenga123")
            
            corbisier = User(
                username="corbisier",
                role="loja",
                store_name="Corbisier"
            )
            corbisier.set_password("corbisier321")
            
            piraporinha = User(
                username="piraporinha",
                role="loja",
                store_name="Piraporinha"
            )
            piraporinha.set_password("piraporinha321")
            
            # Adicionar usuários ao banco de dados
            db.session.add(master)
            db.session.add(alvarenga)
            db.session.add(corbisier)
            db.session.add(piraporinha)
            
            # Commit das alterações
            db.session.commit()
    
    # Configurar login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar blueprints
    from src.routes.auth import auth_bp
    from src.routes.main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app
