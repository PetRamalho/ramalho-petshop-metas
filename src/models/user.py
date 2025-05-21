from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # e.g., alvarenga, corbisier, piraporinha, vinicius
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'master', 'loja'
    store_name = db.Column(db.String(100), nullable=True) # 'Alvarenga', 'Corbisier', 'Piraporinha', or null/empty for master
    # Removed email as it was not specified as a login field or requirement

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'store_name': self.store_name
        }

# --- Outros Modelos --- #

class MetaDiaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key to User table (loja users)
    data = db.Column(db.Date, nullable=False)
    valor_meta = db.Column(db.Float, nullable=False)
    mes = db.Column(db.Integer, nullable=False) # Adicionado: mês da meta (1-12)
    ano = db.Column(db.Integer, nullable=False) # Adicionado: ano da meta

    loja = db.relationship('User', backref=db.backref('metas_diarias', lazy=True))

    def __repr__(self):
        return f'<MetaDiaria {self.loja.store_name} - {self.data} - R${self.valor_meta}>'

class FaturamentoDiario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    valor_faturado = db.Column(db.Float, nullable=False)
    meta_atingida = db.Column(db.Boolean, default=False)

    loja = db.relationship('User', backref=db.backref('faturamentos_diarios', lazy=True))

    def __repr__(self):
        return f'<FaturamentoDiario {self.loja.store_name} - {self.data} - R${self.valor_faturado}>'

class Medalha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loja_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mes = db.Column(db.Integer, nullable=False) # 1-12
    ano = db.Column(db.Integer, nullable=False)
    quantidade = db.Column(db.Integer, default=0)

    loja = db.relationship('User', backref=db.backref('medalhas', lazy=True))

    def __repr__(self):
        return f'<Medalha {self.loja.store_name} - {self.mes}/{self.ano} - {self.quantidade} medalhas>'
