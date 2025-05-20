from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user, logout_user
from src.models.user import User, MetaDiaria, FaturamentoDiario, Medalha, db
from datetime import date, datetime, timedelta
from werkzeug.utils import secure_filename
import os
import pandas as pd
import locale
import calendar
import json

# Configurar pasta de upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tente configurar o locale para português do Brasil
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except:
        pass  # Se não conseguir configurar o locale, usará o padrão

main_bp = Blueprint("main", __name__)

@main_bp.record
def record_params(setup_state):
    app = setup_state.app
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

# Função para obter metas do banco de dados
def obter_metas(mes, ano, loja_id=None):
    """
    Obtém as metas do banco de dados para o mês/ano especificado.
    Se loja_id for fornecido, retorna apenas as metas dessa loja.
    """
    if loja_id:
        metas = MetaDiaria.query.filter_by(
            mes=mes, 
            ano=ano, 
            loja_id=loja_id
        ).all()
    else:
        metas = MetaDiaria.query.filter_by(
            mes=mes, 
            ano=ano
        ).all()
    
    return metas

# Função para obter faturamentos do banco de dados
def obter_faturamentos(mes, ano, loja_id=None):
    """
    Obtém os faturamentos do banco de dados para o mês/ano especificado.
    Se loja_id for fornecido, retorna apenas os faturamentos dessa loja.
    """
    if loja_id:
        faturamentos = FaturamentoDiario.query.filter_by(
            mes=mes, 
            ano=ano, 
            loja_id=loja_id
        ).all()
    else:
        faturamentos = FaturamentoDiario.query.filter_by(
            mes=mes, 
            ano=ano
        ).all()
    
    return faturamentos

# Função para processar dados de metas e faturamentos
def processar_dados_loja(mes, ano, loja_id):
    """
    Processa os dados de metas e faturamentos para uma loja específica.
    Retorna um dicionário com histórico diário e dados de meta mensal.
    """
    # Obter metas e faturamentos do banco de dados
    metas = obter_metas(mes, ano, loja_id)
    faturamentos = obter_faturamentos(mes, ano, loja_id)
    
    # Criar dicionário de metas por dia
    metas_dict = {meta.dia: meta.valor for meta in metas}
    
    # Criar dicionário de faturamentos por dia
    faturamentos_dict = {fat.dia: fat.valor for fat in faturamentos}
    
    # Determinar o número de dias no mês
    num_dias = calendar.monthrange(ano, mes)[1]
    
    # Gerar histórico diário
    historico = []
    acumulado = 0
    
    for dia in range(1, num_dias + 1):
        meta = metas_dict.get(dia, 0)
        faturamento = faturamentos_dict.get(dia, 0)
        
        if faturamento > 0:
            acumulado += faturamento
        
        percentual = round((faturamento / meta) * 100, 1) if meta > 0 else 0
        
        historico.append({
            'dia': dia,
            'faturamento': faturamento,
            'meta': meta,
            'percentual': percentual
        })
    
    # Calcular meta mensal (soma das metas diárias)
    meta_mensal = sum(metas_dict.values())
    
    # Calcular percentual atingido
    percentual = round((acumulado / meta_mensal) * 100, 1) if meta_mensal > 0 else 0
    
    return {
        'historico': historico,
        'meta_mensal': {
            'meta_mensal': meta_mensal,
            'acumulado': acumulado,
            'percentual': percentual
        }
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
    
    # Buscar todas as lojas
    lojas = User.query.filter_by(role="loja").all()
    
    # Processar dados para cada loja
    dados_lojas = {}
    acumulado_grupo = 0
    meta_grupo = 0
    
    for loja in lojas:
        # Processar dados da loja
        dados_loja = processar_dados_loja(selected_month, selected_year, loja.id)
        
        # Adicionar dados ao dicionário
        dados_lojas[loja.id] = dados_loja
        
        # Acumular para o total do grupo
        acumulado_grupo += dados_loja['meta_mensal']['acumulado']
        meta_grupo += dados_loja['meta_mensal']['meta_mensal']
    
    # Calcular percentual do grupo
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
    current_month_num = hoje.month
    current_year = hoje.year
    
    # Obter o dia atual
    dia_atual = hoje.day
    
    # Data formatada para exibição
    data_atual = hoje.strftime("%d/%m/%Y")
    
    # Processar dados da loja atual
    loja_id = current_user.id
    dados_loja = processar_dados_loja(selected_month, selected_year, loja_id)
    
    # Extrair histórico e dados de meta mensal
    historico = dados_loja['historico']
    dados_meta = dados_loja['meta_mensal']
    
    # Dados do dia atual ou último dia com dados
    dados_hoje = next((dia for dia in historico if dia['dia'] == dia_atual), historico[-1] if historico else {'faturamento': 0, 'meta': 0, 'percentual': 0})
    
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
                           current_month_num=current_month_num,
                           current_year=current_year,
                           selected_month=selected_month,
                           selected_year=selected_year,
                           selected_month_name=selected_month_name,
                           historico=historico,
                           historico_json=historico_json,
                           dados_meta=dados_meta,
                           dados_meta_json=dados_meta_json,
                           dados_hoje=dados_hoje,
                           dia_atual=dia_atual)

@main_bp.route("/registrar-faturamento", methods=["POST"])
@login_required
def registrar_faturamento():
    if current_user.role != "loja":
        abort(403) # Forbidden access
    
    # Obter dados do formulário
    dia = request.form.get("dia", type=int)
    faturamento = request.form.get("faturamento", type=float)
    mes = request.form.get("mes", type=int)
    ano = request.form.get("ano", type=int)
    
    # Validar dados
    if not dia or not faturamento or not mes or not ano:
        flash("Dados inválidos. Por favor, tente novamente.", "danger")
        return redirect(url_for("main.dashboard_loja"))
    
    # Verificar se o dia é válido para o mês/ano
    try:
        data = date(ano, mes, dia)
    except ValueError:
        flash("Data inválida. Por favor, tente novamente.", "danger")
        return redirect(url_for("main.dashboard_loja"))
    
    # Verificar se já existe um registro para este dia/mês/ano
    faturamento_existente = FaturamentoDiario.query.filter_by(
        dia=dia,
        mes=mes,
        ano=ano,
        loja_id=current_user.id
    ).first()
    
    if faturamento_existente:
        # Atualizar registro existente
        faturamento_existente.valor = faturamento
        db.session.commit()
        flash(f"Faturamento do dia {dia}/{mes}/{ano} atualizado com sucesso!", "success")
    else:
        # Criar novo registro
        novo_faturamento = FaturamentoDiario(
            dia=dia,
            mes=mes,
            ano=ano,
            valor=faturamento,
            loja_id=current_user.id
        )
        db.session.add(novo_faturamento)
        db.session.commit()
        flash(f"Faturamento do dia {dia}/{mes}/{ano} registrado com sucesso!", "success")
    
    # Verificar se atingiu a meta do dia
    meta = MetaDiaria.query.filter_by(
        dia=dia,
        mes=mes,
        ano=ano,
        loja_id=current_user.id
    ).first()
    
    if meta and faturamento >= meta.valor:
        # Verificar se já existe medalha para este dia
        medalha_existente = Medalha.query.filter_by(
            dia=dia,
            mes=mes,
            ano=ano,
            loja_id=current_user.id
        ).first()
        
        if not medalha_existente:
            # Criar nova medalha
            nova_medalha = Medalha(
                dia=dia,
                mes=mes,
                ano=ano,
                loja_id=current_user.id
            )
            db.session.add(nova_medalha)
            db.session.commit()
            flash(f"Parabéns! Você ganhou uma medalha por atingir a meta do dia {dia}/{mes}/{ano}! 🏆", "success")
    
    return redirect(url_for("main.dashboard_loja", month=mes, year=ano))

@main_bp.route("/admin")
@login_required
def admin():
    if current_user.role != "master":
        abort(403) # Forbidden access
    
    # Buscar metas carregadas (placeholder)
    metas_carregadas = []
    
    return render_template("admin.html", 
                           metas_carregadas=metas_carregadas)

@main_bp.route("/upload-metas", methods=["POST"])
@login_required
def upload_metas():
    if current_user.role != "master":
        abort(403) # Forbidden access
    
    # Verificar se o arquivo foi enviado
    if 'metas_file' not in request.files:
        flash("Nenhum arquivo enviado.", "danger")
        return redirect(url_for("main.admin"))
    
    file = request.files['metas_file']
    
    # Verificar se o arquivo tem nome
    if file.filename == '':
        flash("Nenhum arquivo selecionado.", "danger")
        return redirect(url_for("main.admin"))
    
    # Obter mês e ano selecionados
    mes = request.form.get("mes_meta", type=int)
    ano = request.form.get("ano_meta", type=int)
    
    if not mes or not ano:
        flash("Mês e ano são obrigatórios.", "danger")
        return redirect(url_for("main.admin"))
    
    # Verificar se o arquivo é um Excel
    if file and file.filename.endswith('.xlsx'):
        # Salvar o arquivo temporariamente
        filename = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        try:
            # Processar o arquivo Excel
            xls = pd.ExcelFile(temp_path)
            
            # Verificar se as abas necessárias existem
            required_sheets = ["Alvarenga", "Corbisier", "Piraporinha"]
            missing_sheets = [sheet for sheet in required_sheets if sheet not in xls.sheet_names]
            
            if missing_sheets:
                flash(f"Abas obrigatórias ausentes: {', '.join(missing_sheets)}", "danger")
                os.remove(temp_path)  # Remover arquivo temporário
                return redirect(url_for("main.admin"))
            
            # Mapear nomes de lojas para IDs
            lojas = User.query.filter_by(role="loja").all()
            loja_map = {loja.store_name: loja.id for loja in lojas}
            
            # Processar cada aba
            for sheet_name in required_sheets:
                if sheet_name not in loja_map:
                    flash(f"Loja '{sheet_name}' não encontrada no sistema.", "danger")
                    continue
                
                loja_id = loja_map[sheet_name]
                
                # Ler a aba
                df = pd.read_excel(temp_path, sheet_name=sheet_name)
                
                # Verificar se as colunas necessárias existem
                if 'Dia' not in df.columns or 'Meta' not in df.columns:
                    flash(f"Colunas 'Dia' e 'Meta' obrigatórias ausentes na aba {sheet_name}.", "danger")
                    continue
                
                # Remover metas existentes para este mês/ano/loja
                MetaDiaria.query.filter_by(
                    mes=mes,
                    ano=ano,
                    loja_id=loja_id
                ).delete()
                
                # Inserir novas metas
                for _, row in df.iterrows():
                    if pd.notna(row['Dia']) and pd.notna(row['Meta']):
                        try:
                            dia = int(row['Dia'])
                            meta = float(row['Meta'])
                            
                            # Verificar se o dia é válido
                            if dia < 1 or dia > 31:
                                continue
                            
                            # Criar nova meta
                            nova_meta = MetaDiaria(
                                dia=dia,
                                mes=mes,
                                ano=ano,
                                valor=meta,
                                loja_id=loja_id
                            )
                            db.session.add(nova_meta)
                        except (ValueError, TypeError):
                            # Ignorar linhas com valores inválidos
                            continue
            
            # Commit das alterações
            db.session.commit()
            
            # Remover arquivo temporário
            os.remove(temp_path)
            
            flash(f"Metas para {calendar.month_name[mes]} de {ano} carregadas com sucesso!", "success")
            return redirect(url_for("main.admin"))
            
        except Exception as e:
            flash(f"Erro ao processar o arquivo: {str(e)}", "danger")
            # Remover arquivo temporário em caso de erro
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return redirect(url_for("main.admin"))
    else:
        flash("Formato de arquivo inválido. Por favor, envie um arquivo .xlsx.", "danger")
        return redirect(url_for("main.admin"))

@main_bp.route("/quadro-medalhas/historico")
@login_required
def historico_medalhas():
    # Obter o mês e ano selecionados do parâmetro da URL, ou usar o mês/ano atual como padrão
    hoje = datetime.now()
    selected_month = request.args.get('month', type=int, default=hoje.month)
    selected_year = request.args.get('year', type=int, default=hoje.year)
    
    # Buscar medalhas do mês/ano selecionado
    medalhas = Medalha.query.filter_by(
        mes=selected_month,
        ano=selected_year
    ).all()
    
    # Agrupar medalhas por loja
    medalhas_por_loja = {}
    
    for medalha in medalhas:
        if medalha.loja_id not in medalhas_por_loja:
            medalhas_por_loja[medalha.loja_id] = []
        
        medalhas_por_loja[medalha.loja_id].append(medalha)
    
    # Buscar informações das lojas
    lojas = User.query.filter_by(role="loja").all()
    lojas_dict = {loja.id: loja for loja in lojas}
    
    # Obter o nome do mês em português
    temp_date = datetime(selected_year, selected_month, 1)
    selected_month_name = temp_date.strftime("%B").capitalize()
    
    return render_template("historico_medalhas.html",
                           medalhas_por_loja=medalhas_por_loja,
                           lojas=lojas_dict,
                           selected_month=selected_month,
                           selected_year=selected_year,
                           selected_month_name=selected_month_name)

@main_bp.route("/visualizar-metas")
@login_required
def visualizar_metas():
    if current_user.role != "master":
        abort(403) # Forbidden access
    
    # Obter o mês e ano selecionados do parâmetro da URL
    mes = request.args.get('mes', type=int)
    ano = request.args.get('ano', type=int)
    
    if not mes or not ano:
        flash("Mês e ano são obrigatórios.", "danger")
        return redirect(url_for("main.admin"))
    
    # Buscar metas do mês/ano selecionado
    metas = MetaDiaria.query.filter_by(
        mes=mes,
        ano=ano
    ).all()
    
    # Agrupar metas por loja
    metas_por_loja = {}
    
    for meta in metas:
        if meta.loja_id not in metas_por_loja:
            metas_por_loja[meta.loja_id] = []
        
        metas_por_loja[meta.loja_id].append(meta)
    
    # Buscar informações das lojas
    lojas = User.query.filter_by(role="loja").all()
    lojas_dict = {loja.id: loja for loja in lojas}
    
    # Obter o nome do mês em português
    temp_date = datetime(ano, mes, 1)
    mes_nome = temp_date.strftime("%B").capitalize()
    
    return render_template("visualizar_metas.html",
                           metas_por_loja=metas_por_loja,
                           lojas=lojas_dict,
                           mes=mes,
                           ano=ano,
                           mes_nome=mes_nome)
