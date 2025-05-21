from src import create_app
from src.models.user import db, User, MetaDiaria, FaturamentoDiario, Medalha

app = create_app()

with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    
    # Verificar se já existem usuários
    if User.query.count() == 0:
        # Criar usuário master
        master = User(
            username="adm",
            role="master",
            store_name="Ramalho Pet Shop"
        )
        master.set_password("ramalho2025")
        
        # Criar usuários de loja
        alvarenga = User(
            username="alvarenga",
            role="loja",
            store_name="Alvarenga"
        )
        alvarenga.set_password("alvarenga2025")
        
        corbisier = User(
            username="corbisier",
            role="loja",
            store_name="Corbisier"
        )
        corbisier.set_password("corbisier2025")
        
        piraporinha = User(
            username="piraporinha",
            role="loja",
            store_name="Piraporinha"
        )
        piraporinha.set_password("piraporinha2025")
        
        # Adicionar usuários ao banco de dados
        db.session.add(master)
        db.session.add(alvarenga)
        db.session.add(corbisier)
        db.session.add(piraporinha)
        
        # Commit das alterações
        db.session.commit()
        
        print("Banco de dados inicializado com sucesso!")
        print("Usuários criados:")
        print("- Master: adm / ramalho2025")
        print("- Loja Alvarenga: alvarenga / alvarenga2025")
        print("- Loja Corbisier: corbisier / corbisier2025")
        print("- Loja Piraporinha: piraporinha / piraporinha2025")
    else:
        print("O banco de dados já contém usuários. Nenhum usuário foi criado.")
