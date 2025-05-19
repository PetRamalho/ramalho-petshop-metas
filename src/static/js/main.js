document.addEventListener("DOMContentLoaded", function() {
    // Contador Regressivo para o fim do mês (31/05)
    const contadorElement = document.getElementById("tempo-restante");
    if (contadorElement) {
        const dataFimMes = new Date(new Date().getFullYear(), 4, 31, 23, 59, 59); // Maio é mês 4 (0-indexed)

        function atualizarContador() {
            const agora = new Date();
            const diferenca = dataFimMes - agora;

            if (diferenca < 0) {
                contadorElement.innerHTML = "Prazo encerrado!";
                clearInterval(intervaloContador);
                return;
            }

            const dias = Math.floor(diferenca / (1000 * 60 * 60 * 24));
            const horas = Math.floor((diferenca % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutos = Math.floor((diferenca % (1000 * 60 * 60)) / (1000 * 60));
            const segundos = Math.floor((diferenca % (1000 * 60)) / 1000);

            contadorElement.innerHTML = `${dias}d ${horas}h ${minutos}m ${segundos}s`;
        }

        const intervaloContador = setInterval(atualizarContador, 1000);
        atualizarContador(); // Chamada inicial
    }

    // Frases Inspiradoras Rotativas
    const frasesInspiradoras = [
        "Batemos a meta do dia, não do mês!",
        "Transformando valores em resultados.",
        "Cliente feliz é quem se sente bem desde o ‘bom dia’ até o ‘até logo’.",
        "Fazer o básico com excelência — todos os dias.",
        "Acredite em você e na sua equipe!",
        "Cada passo à frente nos aproxima do sucesso!",
        "A persistência realiza o impossível."
    ];

    const frasePainelElement = document.getElementById("frase-motivacional-painel");
    const fraseFooterElement = document.getElementById("frase-inspiradora");

    function mostrarFraseAleatoria() {
        const indiceAleatorio = Math.floor(Math.random() * frasesInspiradoras.length);
        const frase = frasesInspiradoras[indiceAleatorio];
        if (frasePainelElement) {
            frasePainelElement.textContent = frase;
        }
        if (fraseFooterElement) {
            // fraseFooterElement.textContent = frase; // Decidi manter a frase do footer fixa por enquanto, conforme o base.html inicial
        }
    }

    if (frasePainelElement) {
        mostrarFraseAleatoria();
        setInterval(mostrarFraseAleatoria, 15000); // Muda a cada 15 segundos
    }

    // Placeholder para futuras interações no dashboard, como envio de faturamento
    const formFaturamento = document.getElementById("form-faturamento-diario");
    if (formFaturamento) {
        formFaturamento.addEventListener("submit", function(event) {
            event.preventDefault();
            const faturamento = document.getElementById("faturamento-dia").value;
            console.log("Faturamento do dia registrado (frontend):", faturamento);
            // Aqui viria a lógica para enviar para o backend via fetch/AJAX
            alert("Faturamento de R$ " + faturamento + " registrado! (Simulação Frontend)");
            // Limpar campo ou atualizar UI conforme necessário
        });
    }

    // Simulação de carregamento de dados (a ser substituído por chamadas reais ao backend)
    // Simular dados para o painel da loja
    const lojaMetaDiaria = document.getElementById("loja-meta-diaria");
    const lojaFaturamentoRegistrado = document.getElementById("loja-faturamento-registrado");
    const lojaPercentualAtingido = document.getElementById("loja-percentual-atingido");
    const lojaProgressoDiario = document.getElementById("loja-progresso-diario");
    const lojaAcumuladoMes = document.getElementById("loja-acumulado-mes");

    if (lojaMetaDiaria) lojaMetaDiaria.textContent = "1500,00";
    if (lojaFaturamentoRegistrado) lojaFaturamentoRegistrado.textContent = "750,00";
    if (lojaPercentualAtingido) lojaPercentualAtingido.textContent = "50";
    if (lojaProgressoDiario) {
        lojaProgressoDiario.style.width = "50%";
        lojaProgressoDiario.textContent = "50%";
    }
    if (lojaAcumuladoMes) lojaAcumuladoMes.textContent = "12500,00";

    // Simular dados para o painel master (apenas um exemplo)
    const masterFaturamentoDiarioTotal = document.getElementById("master-faturamento-diario-total");
    if (masterFaturamentoDiarioTotal) masterFaturamentoDiarioTotal.textContent = "5500,00";
    // ... e assim por diante para outros campos do master e das lojas no painel master.

    // Simular Destaques do Dia
    const destaquesContainer = document.getElementById("destaques-do-dia");
    if (destaquesContainer) {
        const destaqueMsg = document.createElement("div");
        destaqueMsg.className = "alerta alerta-sucesso";
        destaqueMsg.textContent = "Parabéns, Loja Exemplo! Meta batida com 103%!";
        //destaquesContainer.appendChild(destaqueMsg); // Mostrar apenas se houver destaque real
    }

    // Simular Alerta de Bônus
    const alertaBonus = document.getElementById("alerta-bonus-equipe");
    // if (alertaBonus) alertaBonus.style.display = "block"; // Mostrar apenas se condição for atingida

    // Simular Quadro de Medalhas
    const quadroMedalhasGeral = document.getElementById("quadro-medalhas-geral");
    if (quadroMedalhasGeral) {
        quadroMedalhasGeral.innerHTML = `
            <div class="loja-medalhas">
                <strong>Alvarenga:</strong> <span class="medalha">🏆</span> <span class="medalha">🏆</span>
            </div>
            <div class="loja-medalhas">
                <strong>Corbisier:</strong> <span class="medalha">🏆</span>
            </div>
            <div class="loja-medalhas">
                <strong>Piraporinha:</strong> (Ainda sem medalhas este mês)
            </div>
        `;
    }

});

// Função para buscar dados do backend (exemplo)
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Falha ao buscar dados:", error);
        return null;
    }
}

// Exemplo de como poderia ser usado para carregar dados do dashboard
// async function carregarPainelLoja() {
//     const dados = await fetchData("/api/painel/loja"); // Endpoint de exemplo
//     if (dados) {
//         document.getElementById("loja-meta-diaria").textContent = dados.meta_diaria;
//         // ... atualizar outros campos
//     }
// }

// if (document.querySelector(".painel-loja")) {
//     carregarPainelLoja();
// }

