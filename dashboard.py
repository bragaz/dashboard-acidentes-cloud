# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E CARREGAMENTO DOS DADOS
# ==============================================================================
st.set_page_config(layout="wide")

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv(
            'acidentes2025_todas_causas_tipos.csv',
            delimiter=';',
            encoding='latin1'
        )

        # --- Limpeza e Preparação dos Dados ---
        df['data_hora'] = pd.to_datetime(df['data_inversa'] + ' ' + df['horario'], errors='coerce')
        df.dropna(subset=['data_hora'], inplace=True)

        # --- FILTRAR PARA OS ÚLTIMOS 6 MESES ---
        data_mais_recente = df['data_hora'].max()
        data_inicio_6_meses = data_mais_recente - pd.DateOffset(months=6)
        df = df[df['data_hora'] >= data_inicio_6_meses].copy()

        df['latitude'] = df['latitude'].str.replace(',', '.').astype(float)
        df['longitude'] = df['longitude'].str.replace(',', '.').astype(float)
        df.dropna(subset=['latitude', 'longitude'], inplace=True)

        df['hora'] = df['data_hora'].dt.hour
        df['mes_num'] = df['data_hora'].dt.month
        nomes_meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        df['mes'] = df['mes_num'].map(nomes_meses)

        df['mortos'] = pd.to_numeric(df['mortos'], errors='coerce').fillna(0).astype(int)

        return df
    except FileNotFoundError:
        st.error("Arquivo 'acidentes2025_todas_causas_tipos.csv' não foi encontrado. Verifique se ele está na mesma pasta que o script do dashboard.")
        return None

df_acidentes = carregar_dados()

# ==============================================================================
# 3. CONSTRUÇÃO DA INTERFACE DO DASHBOARD
# ==============================================================================
if df_acidentes is not None:
    st.sidebar.header("Filtros Interativos")

    # Filtro por Estado (UF)
    lista_ufs = sorted(df_acidentes['uf'].unique())
    uf_selecionada = st.sidebar.multiselect(
        'Selecione o Estado (UF):',
        options=lista_ufs,
        default=lista_ufs
    )

    # NOVO: Filtro por Município (selectbox com "TODOS")
    municipios_filtrados = df_acidentes[df_acidentes['uf'].isin(uf_selecionada)]['municipio'].unique()
    lista_municipios = ['TODOS'] + sorted(municipios_filtrados)
    municipio_selecionado = st.sidebar.selectbox(
        "Selecione o Município:",
        options=lista_municipios
    )

    # Filtro por Mês
    meses_disponiveis = sorted(
        df_acidentes['mes'].unique(),
        key=lambda x: list(pd.to_datetime(df_acidentes['data_hora']).dt.month.unique())
    )
    mes_selecionado = st.sidebar.multiselect(
        "Selecione o Mês:",
        options=meses_disponiveis,
        default=meses_disponiveis
    )

    # Filtro por Causa
    lista_causas = ['TODAS'] + sorted(df_acidentes['causa_acidente'].unique())
    causa_selecionada = st.sidebar.selectbox(
        'Selecione a Causa do Acidente:',
        options=lista_causas
    )

    # --- Aplicação dos Filtros ---
    df_filtrado = df_acidentes.copy()

    if uf_selecionada:
        df_filtrado = df_filtrado[df_filtrado['uf'].isin(uf_selecionada)]

    if municipio_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_selecionado]

    if mes_selecionado:
        df_filtrado = df_filtrado[df_filtrado['mes'].isin(mes_selecionado)]

    if causa_selecionada != 'TODAS':
        df_filtrado = df_filtrado[df_filtrado['causa_acidente'] == causa_selecionada]

    # --- Título e Métricas ---
    st.title("Dashboard de Análise de Acidentes de Trânsito 🚗")
    st.markdown("Análise dos **últimos 6 meses** de dados. Use os filtros para explorar.")

    st.markdown("### Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    total_acidentes = df_filtrado.shape[0]
    total_mortos = df_filtrado['mortos'].sum()
    taxa_mortalidade = (total_mortos / total_acidentes) * 100 if total_acidentes > 0 else 0

    col1.metric("Total de Acidentes", f"{total_acidentes:,}".replace(",", "."))
    col2.metric("Total de Vítimas Fatais", f"{total_mortos:,}".replace(",", "."))
    col3.metric("Mortalidade (%)", f"{taxa_mortalidade:.2f}%")

    # --- Mapa ---
    st.markdown("---")
    st.markdown("### 🗺️ Mapa de Concentração de Acidentes")
    if not df_filtrado.empty:
        df_mapa = df_filtrado[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        st.map(df_mapa, zoom=3)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")

    # --- Gráficos ---
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("### 🕒 Acidentes por Hora do Dia")
        if not df_filtrado.empty:
            acidentes_por_hora = df_filtrado['hora'].value_counts().sort_index()
            fig_hora = px.bar(
                acidentes_por_hora,
                x=acidentes_por_hora.index,
                y=acidentes_por_hora.values,
                labels={'x': 'Hora do Dia', 'y': 'Número de Acidentes'},
                title="Distribuição de Acidentes ao Longo do Dia"
            )
            fig_hora.update_layout(xaxis_title="Hora", yaxis_title="Nº de Acidentes")
            st.plotly_chart(fig_hora, use_container_width=True)
        else:
            st.warning("Sem dados para exibir.")

    with col_graf2:
        st.markdown("### ❗ Top 10 Causas de Acidentes")
        if not df_filtrado.empty:
            top_10_causas = df_filtrado['causa_acidente'].value_counts().nlargest(10)
            fig_causas = px.bar(
                top_10_causas,
                x=top_10_causas.values,
                y=top_10_causas.index,
                orientation='h',
                labels={'x': 'Número de Acidentes', 'y': 'Causa do Acidente'},
                title="As 10 Causas Mais Comuns de Acidentes"
            )
            fig_causas.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_causas, use_container_width=True)
        else:
            st.warning("Sem dados para exibir.")

    # --- Tabela ---
    st.markdown("---")
    st.markdown("### Dados Detalhados")
    st.write("Veja os dados brutos correspondentes aos filtros aplicados:")
    st.dataframe(df_filtrado[['data_hora', 'mes', 'uf', 'municipio', 'causa_acidente', 'tipo_acidente', 'mortos']].head(100))
