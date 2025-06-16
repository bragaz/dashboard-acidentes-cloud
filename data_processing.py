# data_processing.py

import pandas as pd
import streamlit as st
from datetime import datetime

@st.cache_data
def carregar_dados():
    """
    Carrega, limpa e pré-processa os dados de acidentes.
    Filtra para os últimos 6 meses e prepara colunas para visualização.
    """
    try:
        # ATENÇÃO: Substitua 'acidentes2025_todas_causas_tipos.csv' pela URL do seu arquivo no Azure Blob Storage
        # Exemplo: url_azure_blob = 'https://suacontadearmazenamento.blob.core.windows.net/seubucket/acidentes2025_todas_causas_tipos.csv'
        # df = pd.read_csv(url_azure_blob, delimiter=';', encoding='latin1')
        df = pd.read_csv(
            'acidentes2025_todas_causas_tipos.csv', # REMOVA ESTA LINHA E DESCOMENTE A LINHA ACIMA APÓS FAZER O UPLOAD PARA O AZURE
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
        st.error("Arquivo de dados não encontrado. Verifique se a URL do Azure Blob Storage está correta ou se o arquivo local existe.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar ou processar os dados: {e}")
        return None