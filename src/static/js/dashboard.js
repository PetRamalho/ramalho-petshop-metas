// dashboard.js - Script para o painel de metas do Ramalho Pet Shop

document.addEventListener('DOMContentLoaded', function() {
    // Contador regressivo
    atualizarContadorRegressivo();
    setInterval(atualizarContadorRegressivo, 1000);
    
    // Frases motivacionais
    rotacionarFrasesMotivacionais();
    
    // Inicializar dados do painel master (se existir)
    if (document.querySelector('.painel-master')) {
        inicializarPainelMaster();
    }
    
    // Inicializar dados do painel da loja (se existir)
    if (document.querySelector('.painel-loja')) {
        inicializarPainelLoja();
    }
});

// Função para atualizar o contador regressivo
function atualizarContadorRegressivo() {
    const contadorElement = document.getElementById('tempo-restante');
    if (!contadorElement) return;
    
    const agora = new Date();
    const ultimoDiaMes = new Date(agora.getFullYear(), agora.getMonth() + 1, 0, 23, 59, 59);
    const diferenca = ultimoDiaMes - agora;
    
    // Calcular dias, horas, minutos e segundos
    const dias = Math.floor(diferenca / (1000 * 60 * 60 * 24));
    const horas = Math.floor((diferenca % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutos = Math.floor((diferenca % (1000 * 60 * 60)) / (1000 * 60));
    const segundos = Math.floor((diferenca % (1000 * 60)) / 1000);
    
    contadorElement.textContent = `${dias}d ${horas}h ${minutos}m ${segundos}s`;
}

// Função para rotacionar frases motivacionais
function rotacionarFrasesMotivacionais() {
    const frases = [
        "Batemos a meta do dia, não do mês",
        "Transformando valores em resultados",
        "Cliente feliz é quem se sente bem desde o 'bom dia' até o 'até logo'",
        "Fazer o básico com excelência — todos os dias"
    ];
    
    const fraseElement = document.getElementById('frase-motivacional-painel');
    if (!fraseElement) return;
    
    let indice = 0;
    
    // Definir a primeira frase
    fraseElement.textContent = frases[indice];
    
    // Rotacionar frases a cada 10 segundos
    setInterval(() => {
        indice = (indice + 1) % frases.length;
        fraseElement.textContent = frases[indice];
    }, 10000);
}

// Função para inicializar o painel master
function inicializarPainelMaster() {
    // Verificar se temos dados das lojas em formato JSON
    const dadosLojasElement = document.getElementById('dados-lojas-json');
    if (!dadosLojasElement) return;
    
    try {
        // Obter dados das lojas do atributo data
        const dadosLojas = JSON.parse(dadosLojasElement.textContent);
        
        // Para cada loja, preencher a tabela de histórico e o gráfico
        for (const lojaId in dadosLojas) {
            preencherHistoricoDiario(lojaId, dadosLojas[lojaId].historico);
            atualizarGraficoMetaMensal(lojaId, dadosLojas[lojaId].meta_mensal);
        }
        
        // Atualizar o gráfico do grupo
        const metaGrupoElement = document.getElementById('meta-grupo');
        const acumuladoGrupoElement = document.getElementById('acumulado-grupo');
        const percentualGrupoElement = document.getElementById('percentual-grupo');
        
        if (metaGrupoElement && acumuladoGrupoElement && percentualGrupoElement) {
            const metaGrupo = parseFloat(metaGrupoElement.textContent);
            const acumuladoGrupo = parseFloat(acumuladoGrupoElement.textContent);
            const percentualGrupo = parseFloat(percentualGrupoElement.textContent);
            
            document.getElementById('meta-mensal-grupo').textContent = formatarValor(metaGrupo);
            document.getElementById('acumulado-mensal-grupo').textContent = formatarValor(acumuladoGrupo);
            document.getElementById('percentual-meta-grupo').textContent = percentualGrupo;
            document.getElementById('barra-acumulado-grupo').style.width = `${Math.min(percentualGrupo, 100)}%`;
        }
        
    } catch (error) {
        console.error('Erro ao processar dados das lojas:', error);
    }
}

// Função para preencher a tabela de histórico diário
function preencherHistoricoDiario(lojaId, historico) {
    const tbody = document.getElementById(`historico-diario-${lojaId}`);
    if (!tbody) return;
    
    // Limpar conteúdo atual
    tbody.innerHTML = '';
    
    // Preencher com os dados do histórico
    historico.forEach(dia => {
        const tr = document.createElement('tr');
        
        // Criar células
        const tdDia = document.createElement('td');
        tdDia.textContent = dia.dia;
        
        const tdFaturamento = document.createElement('td');
        tdFaturamento.textContent = `R$ ${formatarValor(dia.faturamento)}`;
        
        const tdMeta = document.createElement('td');
        tdMeta.textContent = `R$ ${formatarValor(dia.meta)}`;
        
        const tdPercentual = document.createElement('td');
        tdPercentual.textContent = `${dia.percentual}%`;
        
        // Adicionar classe de destaque se atingiu a meta
        if (dia.percentual >= 100) {
            tdPercentual.classList.add('meta-atingida');
        } else {
            tdPercentual.classList.add('meta-nao-atingida');
        }
        
        // Adicionar células à linha
        tr.appendChild(tdDia);
        tr.appendChild(tdFaturamento);
        tr.appendChild(tdMeta);
        tr.appendChild(tdPercentual);
        
        // Adicionar linha à tabela
        tbody.appendChild(tr);
    });
    
    // Se não houver dados, mostrar mensagem
    if (historico.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = 4;
        td.textContent = 'Nenhum dado disponível para o período selecionado.';
        td.style.textAlign = 'center';
        tr.appendChild(td);
        tbody.appendChild(tr);
    }
}

// Função para atualizar o gráfico de meta mensal vs. acumulado
function atualizarGraficoMetaMensal(lojaId, dados) {
    // Atualizar valores
    document.getElementById(`meta-mensal-${lojaId}`).textContent = formatarValor(dados.meta_mensal);
    document.getElementById(`acumulado-mensal-${lojaId}`).textContent = formatarValor(dados.acumulado);
    document.getElementById(`percentual-meta-${lojaId}`).textContent = dados.percentual;
    
    // Atualizar barra de progresso
    document.getElementById(`barra-acumulado-${lojaId}`).style.width = `${Math.min(dados.percentual, 100)}%`;
}

// Função para inicializar o painel da loja
function inicializarPainelLoja() {
    // Implementar lógica específica para o painel da loja
    // (similar ao painel master, mas com foco apenas na loja atual)
}

// Função auxiliar para formatar valores monetários
function formatarValor(valor) {
    return valor.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}
