from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from src.models.user import User, MetaDiaria, FaturamentoDiario, Medalha, db # Import all necessary models
from datetime import date, datetime
import locale

# Tente configurar o locale para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except:
        pass  # Se não conseguir configurar o locale, usará o padrão

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "master":
            return redirect(url_for("main.dashboard_master"))
        else:
            return redirect(url_for("main.dashboard_loja"))
    return redirect(url_for("auth.login")) # Redirect to login if not authenticated

@main_bp.route("/dashboard") # A generic dashboard route that redirects
@login_required
def dashboard():
    if current_user.role == "master":
        return redirect(url_for("main.dashboard_master"))
    elif current_user.role == "loja":
        return redirect(url_for("main.dashboard_loja"))
    else:
        # Should not happen with proper roles
        logout_user()
        flash("Perfil de usuário inválido.", "danger")
        return redirect(url_for("auth.login"))

@main_bp.route("/dashboard/master")
@login_required
def dashboard_master():
    if current_user.role != "master":
        abort(403) # Forbidden access
    
    # Fetch data for master dashboard (consolidated and per store)
    # This is a placeholder, actual data fetching will be more complex
    lojas = User.query.filter_by(role="loja").all()
    
    # Obter o mês atual em português
    current_month = datetime.now().strftime("%B de %Y").capitalize()
    
    # Pass any necessary data to the template
    return render_template("dashboard.html", 
                          usuario_master=True, 
                          lojas=lojas, 
                          nome_usuario=current_user.username,
                          current_month=current_month)

@main_bp.route("/dashboard/loja")
@login_required
def dashboard_loja():
    if current_user.role != "loja":
        abort(403) # Forbidden access
    
    # Fetch data specific to this store
    # This is a placeholder
    data_atual = date.today().strftime("%d/%m/%Y")
    
    # Obter o mês atual em português
    current_month = datetime.now().strftime("%B de %Y").capitalize()
    
    # Pass any necessary data to the template
    return render_template("dashboard.html", 
                           usuario_loja=True, 
                           nome_loja=current_user.store_name, 
                           nome_usuario=current_user.username,
                           data_atual=data_atual,
                           current_month=current_month)

@main_bp.route("/quadro-medalhas/historico")
@login_required
def historico_medalhas():
    # Placeholder for historico de medalhas page
    # Fetch medal history data from DB
    # For now, just render a simple template or redirect
    return render_template("historico_medalhas.html") # Needs this template created

# Add other main application routes here (e.g., admin panel for master user)
