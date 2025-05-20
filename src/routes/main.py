from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user, logout_user
from src.models.user import User, MetaDiaria, FaturamentoDiario, Medalha, db # Import all necessary models
from datetime import date, datetime
import locale
import calendar

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
    
    # Obter o mês e ano selecionados do parâmetro da URL, ou usar o mês/ano atual como padrão
    hoje = datetime.now()
    selected_month = request.args.get('month', type=int, default=hoje.month)
    selected_year = request.args.get('year', type=int, default=hoje.year)
    
    # Validar mês e ano
    if selected_month < 1 or selected_month > 12:
        selected_month = hoje.month
    if selected_year < 2024 or selected_year > 2030:  # Ajuste o intervalo conforme necessário
        selected_year = hoje.year
    
    # Obter o nome do mês em português
    # Criar uma data com o mês selecionado para obter o nome do mês
    temp_date = datetime(selected_year, selected_month, 1)
    selected_month_name = temp_date.strftime("%B").capitalize()
    
    # Obter o mês atual em português (para o indicador de mês vigente)
    current_month = hoje.strftime("%B de %Y").capitalize()
    
    # Fetch data for master dashboard (consolidated and per store)
    # This is a placeholder, actual data fetching will be more complex
    lojas = User.query.filter_by(role="loja").all()
    
    # Pass any necessary data to the template
    return render_template("dashboard.html", 
                          usuario_master=True, 
                          lojas=lojas, 
                          nome_usuario=current_user.username,
                          current_month=current_month,
                          selected_month=selected_month,
                          selected_year=selected_year,
                          selected_month_name=selected_month_name)

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

