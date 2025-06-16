# app.py

import streamlit as st
import pandas as pd
from data_processing import carregar_dados # Importa a função do outro arquivo
from visualizations import plotar_mapa, plotar_acidentes_por_hora, plotar_top_causas, exibir_dados_detalhados # Importa as funções de visualização
import logging

# ==============================================================================
# 1. Configuração de Logs
# ==============================================================================
# No topo do seu app.py
# Para ambiente local ou para o Streamlit Community Cloud, o básico é suficiente.
# Para Azure Application Insights, você precisaria adicionar o código de integração aqui.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E CARREGAMENTO DOS DADOS
# ==============================================================================
st.set_page_config(layout="wide", page_title="Dashboard de Acidentes de Trânsito", page_icon="🚗")

df_acidentes = carregar_dados()

# ==============================================================================
# 3. INTERFACE DO DASHBOARD E LÓGICA DOS FILTROS
# ==============================================================================
if df_acidentes is not None:
    st.sidebar.header("Filtros Interativos")
    logging.info("Dashboard iniciado e dados carregados com sucesso.")

    # Filtro por Estado (UF)
    lista_ufs = sorted(df_acidentes['uf'].unique())
    uf_selecionada = st.sidebar.multiselect(
        'Selecione o Estado (UF):',
        options=lista_ufs,
        default=lista_ufs
    )
    logging.info(f"Filtro de UF selecionado: {uf_selecionada}")

    # Filtro por Município
    municipios_filtrados = df_acidentes[df_acidentes['uf'].isin(uf_selecionada)]['municipio'].unique() if uf_selecionada else df_acidentes['municipio'].unique()
    lista_municipios = ['TODOS'] + sorted(municipios_filtrados)
    municipio_selecionado = st.sidebar.selectbox(
        "Selecione o Município:",
        options=lista_municipios
    )
    logging.info(f"Filtro de Município selecionado: {municipio_selecionado}")


    # Filtro por Mês
    # Para garantir a ordem correta dos meses, filtramos pelos meses presentes nos dados
    meses_disponiveis_df = df_acidentes[['mes_num', 'mes']].drop_duplicates().sort_values('mes_num')['mes'].tolist()

    mes_selecionado = st.sidebar.multiselect(
        "Selecione o Mês:",
        options=meses_disponiveis_df,
        default=meses_disponiveis_df
    )
    logging.info(f"Filtro de Mês selecionado: {mes_selecionado}")

    # Filtro por Causa
    lista_causas = ['TODAS'] + sorted(df_acidentes['causa_acidente'].unique())
    causa_selecionada = st.sidebar.selectbox(
        'Selecione a Causa do Acidente:',
        options=lista_causas
    )
    logging.info(f"Filtro de Causa selecionado: {causa_selecionada}")

    # --- Aplicação dos Filtros ---
    df_filtrado = df_acidentes.copy()

    if uf_selecionada:
        df_filtrado = df_filtrado[df_filtrado['uf'].isin(uf_selecionada)]

    if municipio_selecionado != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['municipio'] == municipio_selecionado]

    if mes_selecionado:
        df_filtrado = df_filtrado[df_filtrado['mes'].isin(mes_selecionado)]

    if causa_selecionada != 'TODOS':
        df_filtrado = df_filtrado[df_filtrado['causa_acidente'] == causa_selecionada]
    
    logging.info(f"Dados filtrados. Total de registros após filtros: {len(df_filtrado)}")

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
    logging.info(f"Métricas calculadas: Acidentes={total_acidentes}, Mortos={total_mortos}, Taxa Mortalidade={taxa_mortalidade:.2f}%")


    # --- Chamadas das Funções de Visualização ---
    plotar_mapa(df_filtrado)

    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        plotar_acidentes_por_hora(df_filtrado)
    with col_graf2:
        plotar_top_causas(df_filtrado)
    
    exibir_dados_detalhados(df_filtrado)

else:
    st.error("Não foi possível carregar os dados. Verifique o arquivo `data_processing.py` e o caminho/URL do arquivo CSV.")
    logging.error("Falha no carregamento inicial dos dados.")