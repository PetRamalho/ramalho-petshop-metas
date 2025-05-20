from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user, logout_user
from src.models.user import User, MetaDiaria, FaturamentoDiario, Medalha, db # Import all necessary models
from datetime import date, datetime, timedelta
import locale
import calendar
import random
import json

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

# Função auxiliar para gerar dados simulados de histórico diário
def gerar_dados_historico(mes, ano, loja_id):
    dados = []
    # Determinar o número de dias no mês
    num_dias = calendar.monthrange(ano, mes)[1]
    
    # Gerar dados para cada dia do mês até o dia atual (se for o mês atual)
    hoje = datetime.now()
    ultimo_dia = num_dias
    if mes == hoje.month and ano == hoje.year:
        ultimo_dia = hoje.day
    
    # Metas diárias simuladas por loja
    metas_diarias = {
        1: 6000,  # Alvarenga
        2: 5500,  # Corbisier
        3: 5000   # Piraporinha
    }
    
    meta_diaria = metas_diarias.get(loja_id, 5500)  # Valor padrão se loja_id não existir
    
    for dia in range(1, ultimo_dia + 1):
        # Simular faturamento entre 80% e 120% da meta
        faturamento = round(meta_diaria * (0.8 + random.random() * 0.4), 2)
        percentual = round((faturamento / meta_diaria) * 100, 1)
        
        dados.append({
            'dia': dia,
            'faturamento': faturamento,
            'meta': meta_diaria,
            'percentual': percentual
        })
    
    return dados

# Função auxiliar para gerar dados simulados de meta mensal e acumulado
def gerar_dados_meta_mensal(mes, ano, loja_id):
    # Metas mensais simuladas por loja
    metas_mensais = {
        1: 180000,  # Alvarenga
        2: 165000,  # Corbisier
        3: 150000   # Piraporinha
    }
    
    # Meta total do grupo
    meta_grupo = 580000
    
    # Meta da loja específica ou valor padrão
    meta_mensal = metas_mensais.get(loja_id, 165000)
    
    # Calcular acumulado com base nos dados diários
    dados_diarios = gerar_dados_historico(mes, ano, loja_id)
    acumulado = sum(dia['faturamento'] for dia in dados_diarios)
    
    # Calcular percentual atingido
    percentual = round((acumulado / meta_mensal) * 100, 1) if meta_mensal > 0 else 0
    
    return {
        'meta_mensal': meta_mensal,
        'acumulado': acumulado,
        'percentual': percentual,
        'meta_grupo': meta_grupo
    }

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
    
    # Gerar dados simulados para cada loja
    dados_lojas = {}
    acumulado_grupo = 0
    
    for loja in lojas:
        # Gerar histórico diário
        historico = gerar_dados_historico(selected_month, selected_year, loja.id)
        
        # Gerar dados de meta mensal
        dados_meta = gerar_dados_meta_mensal(selected_month, selected_year, loja.id)
        
        # Adicionar dados ao dicionário
        dados_lojas[loja.id] = {
            'historico': historico,
            'meta_mensal': dados_meta
        }
        
        # Acumular para o total do grupo
        acumulado_grupo += dados_meta['acumulado']
    
    # Calcular percentual do grupo
    meta_grupo = 580000  # Meta total do grupo
    percentual_grupo = round((acumulado_grupo / meta_grupo) * 100, 1) if meta_grupo > 0 else 0
    
    # Converter dados para JSON para uso no JavaScript
    dados_lojas_json = json.dumps(dados_lojas)
    
    # Pass any necessary data to the template
    return render_template("dashboard.html", 
                          usuario_master=True, 
                          lojas=lojas, 
                          nome_usuario=current_user.username,
                          current_month=current_month,
                          selected_month=selected_month,
                          selected_year=selected_year,
                          selected_month_name=selected_month_name,
                          dados_lojas=dados_lojas,
                          dados_lojas_json=dados_lojas_json,
                          acumulado_grupo=acumulado_grupo,
                          meta_grupo=meta_grupo,
                          percentual_grupo=percentual_grupo)

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
    
    # Gerar dados simulados para a loja atual
    hoje = datetime.now()
    loja_id = current_user.id
    
    # Gerar histórico diário
    historico = gerar_dados_historico(hoje.month, hoje.year, loja_id)
    
    # Gerar dados de meta mensal
    dados_meta = gerar_dados_meta_mensal(hoje.month, hoje.year, loja_id)
    
    # Dados do dia atual (último dia do histórico)
    dados_hoje = historico[-1] if historico else {'faturamento': 0, 'meta': 0, 'percentual': 0}
    
    # Converter dados para JSON para uso no JavaScript
    historico_json = json.dumps(historico)
    dados_meta_json = json.dumps(dados_meta)
    
    # Pass any necessary data to the template
    return render_template("dashboard.html", 
                           usuario_loja=True, 
                           nome_loja=current_user.store_name, 
                           nome_usuario=current_user.username,
                           data_atual=data_atual,
                           current_month=current_month,
                           historico=historico,
                           historico_json=historico_json,
                           dados_meta=dados_meta,
                           dados_meta_json=dados_meta_json,
                           dados_hoje=dados_hoje)

@main_bp.route("/quadro-medalhas/historico")
@login_required
def historico_medalhas():
    # Placeholder for historico de medalhas page
    # Fetch medal history data from DB
    # For now, just render a simple template or redirect
    return render_template("historico_medalhas.html") # Needs this template created

# Add other main application routes here (e.g., admin panel for master user)
