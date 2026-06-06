import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA WEB
st.set_page_config(
    page_title="Portal de Produção Industrial",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título Principal do Site
st.title("🏭 Painel de Controle de Produção Operacional")
st.markdown("---")

# 2. CARREGAMENTO DOS DADOS (Otimizado para Servidores Web)
@st.cache_data
def carregar_dados_producao():
    dados = {
        "Hora": ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00"] * 2,
        "Turno": ["Turno A"] * 6 + ["Turno B"] * 6,
        "Maquina": ["Injetora 01"] * 6 + ["Corte CNC"] * 6,
        "Pecas_Boas": [150, 180, 210, 90, 195, 200, 380, 410, 420, 150, 400, 430],
        "Refugo": [2, 1, 8, 0, 3, 4, 1, 2, 12, 0, 3, 2],
        "Tempo_Disponivel_Min": [60] * 12,
        "Tempo_Parado_Min": [0, 5, 15, 40, 0, 0, 0, 0, 20, 45, 5, 0],
        "Motivo_Parada": ["Nenhum", "Ajuste", "Troca de Molde", "Manutencao", "Nenhum", "Nenhum", 
                          "Nenhum", "Nenhum", "Limpeza", "Quebra de Correia", "Ajuste", "Nenhum"]
    }
    df = pd.DataFrame(dados)
    
    # Cálculos operacionais para métricas (OEE / Qualidade)
    df["Tempo_Rodando_Min"] = df["Tempo_Disponivel_Min"] - df["Tempo_Parado_Min"]
    df["Disponibilidade_Pct"] = (df["Tempo_Rodando_Min"] / df["Tempo_Disponivel_Min"]) * 100
    return df

df_producao = carregar_dados_producao()

# 3. BARRA LATERAL INTERATIVA (Filtros do Usuário no Site)
st.sidebar.header("🔍 Filtros de Produção")

# Filtro de Turno
lista_turnos = ["Todos"] + list(df_producao["Turno"].unique())
turno_selecionado = st.sidebar.selectbox("Selecione o Turno:", lista_turnos)

# Filtro de Máquina
lista_maquinas = ["Todas"] + list(df_producao["Maquina"].unique())
maquina_selecionada = st.sidebar.selectbox("Selecione a Máquina:", lista_maquinas)

st.sidebar.markdown("---")
st.sidebar.header("🎯 Gestão de Metas")
# Controle dinâmico para o utilizador simular metas no site
meta_pecas = st.sidebar.slider("Meta de Peças Boas para o Período:", min_value=500, max_value=5000, value=2000, step=100)

# Aplicação dos filtros na base de dados ativa
df_filtrado = df_producao.copy()
if turno_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Turno"] == turno_selecionado]
if maquina_selecionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Maquina"] == maquina_selecionada]


# 4. PROCESSAMENTO DE MÉTRICAS GLOBAIS
total_boas = df_filtrado["Pecas_Boas"].sum()
total_refugo = df_filtrado["Refugo"].sum()
total_produzido = total_boas + total_refugo

taxa_refugo = (total_refugo / total_produzido * 100) if total_produzido > 0 else 0
oee_medio_disp = df_filtrado["Disponibilidade_Pct"].mean()


# 5. CARTÕES INDICADORES DE PERFORMANCE (KPIs)
card1, card2, card3 = st.columns(3)

with card1:
    st.metric(label="📈 Disponibilidade Média (OEE)", value=f"{oee_medio_disp:.1f}%")

with card2:
    st.metric(label="📦 Peças Boas Produzidas", value=f"{total_boas:,}".replace(",", "."))

with card3:
    st.metric(label="🗑️ Taxa de Refugo", value=f"{taxa_refugo:.2f}%")

# Sistema de alertas visuais automáticos do site
if taxa_refugo > 2.0:
    st.error(f"🚨 **Alerta Operacional:** A taxa de refugo está crítica ({taxa_refugo:.2f}%)! Verifique os parâmetros técnicos.")
else:
    st.success("✅ **Controle de Qualidade:** Taxa de refugo estável e dentro dos limites tolerados.")

st.markdown("---")


# 6. MONITORIZAÇÃO DA META EM TEMPO REAL
st.subheader("📊 Progresso em Relação à Meta Definida")
porcentagem_meta = min(total_boas / meta_pecas, 1.0) # Proteção visual para não quebrar a barra se passar de 100%
st.progress(porcentagem_meta)
st.write(f"O período atual atingiu **{total_boas / meta_pecas * 100:.1f}%** da meta estipulada de {meta_pecas:,} unidades.".replace(",", "."))

st.markdown("---")


# 7. GRÁFICOS INTERATIVOS WEB
col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.subheader("Evolução da Produção Hora a Hora")
    fig_linha = px.line(
        df_filtrado,
        x="Hora",
        y="Pecas_Boas",
        color="Maquina",
        markers=True,
        labels={"Pecas_Boas": "Peças Boas", "Hora": "Horário da Coleta"},
        template="plotly_white"
    )
    st.plotly_chart(fig_linha, use_container_width=True)

with col_grafico2:
    st.subheader("Análise de Motivos de Parada")
    df_paradas = df_filtrado[df_filtrado["Tempo_Parado_Min"] > 0]
    
    if not df_paradas.empty:
        fig_pizza = px.pie(
            df_paradas, 
            values="Tempo_Parado_Min", 
            names="Motivo_Parada",
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("Nenhum registro de parada para a combinação de filtros selecionada.")