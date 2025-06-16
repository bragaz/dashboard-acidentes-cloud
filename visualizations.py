# visualizations.py

import streamlit as st
import plotly.express as px
import pandas as pd

def plotar_mapa(df_filtrado: pd.DataFrame):
    """
    Gera e exibe um mapa de concentração de acidentes usando Streamlit.
    """
    st.markdown("### 🗺️ Mapa de Concentração de Acidentes")
    if not df_filtrado.empty:
        df_mapa = df_filtrado[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        st.map(df_mapa, zoom=3)
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados no mapa.")

def plotar_acidentes_por_hora(df_filtrado: pd.DataFrame):
    """
    Gera e exibe um gráfico de barras de acidentes por hora do dia.
    """
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
        st.warning("Sem dados para exibir o gráfico de acidentes por hora.")

def plotar_top_causas(df_filtrado: pd.DataFrame):
    """
    Gera e exibe um gráfico de barras das top 10 causas de acidentes.
    """
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
        st.warning("Sem dados para exibir o gráfico de top 10 causas.")

def exibir_dados_detalhados(df_filtrado: pd.DataFrame):
    """
    Exibe uma tabela com os dados detalhados.
    """
    st.markdown("---")
    st.markdown("### Dados Detalhados")
    st.write("Veja os dados brutos correspondentes aos filtros aplicados:")
    st.dataframe(df_filtrado[['data_hora', 'mes', 'uf', 'municipio', 'causa_acidente', 'tipo_acidente', 'mortos']].head(100))