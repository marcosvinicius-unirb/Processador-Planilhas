import streamlit as st
import pandas as pd
import io

# --------------------------------------------------------------------------
# --- 1. FUNÇÕES DE ESTILO (Com as novas cores) ---
# --------------------------------------------------------------------------

def destacar_vazios(val):
    """
    Pinta o fundo de vermelho claro se a célula for Nula (NaN).
    """
    cor = ''
    if pd.isna(val) or val == '':
        cor = 'background-color: #FFCDD2' # Vermelho claro
    return cor

def zebra_stripes(row):
    """
    Aplica cores de fundo alternadas (tons de azul)
    e garante que o texto da célula seja preto.
    """
    # Cor 1: #8DB4E2
    cor_fundo1 = 'background-color: #8DB4E2; color: black;'
    # Cor 2: #DCE6F1
    cor_fundo2 = 'background-color: #DCE6F1; color: black;'

    if row.name % 2 == 0:
        return [cor_fundo1] * len(row) # Linha par
    else:
        return [cor_fundo2] * len(row) # Linha ímpar

# --- Estilo do Cabeçalho (Nova Cor) ---
header_style = {
    'selector': 'th.col_heading', # 'th' é o elemento do cabeçalho
    'props': [
        ('background-color', '#538DD5'), # Novo azul do cabeçalho
        ('color', 'white'),             # Letras brancas
        ('font-weight', 'bold')
    ]
}


# --------------------------------------------------------------------------
# --- 2. INTERFACE DO APLICATIVO WEB (STREAMLIT) ---
# --------------------------------------------------------------------------

# Configurações da página (título que aparece na aba do navegador)
st.set_page_config(page_title="Processador de Planilhas", layout="centered")

# Título principal do aplicativo
st.title("🚀 Processador de Planilhas de Alunos")
st.write("Esta aplicação cruza a planilha de cobranças com a de CPFs, insere a nova coluna e aplica a formatação visual.")

# --- 2.1. Upload dos Arquivos ---

file_cobrancas = st.file_uploader(
    "1. Faça o upload da planilha de COBRANÇAS (.xlsx)",
    type="xlsx"
)

file_cpfs = st.file_uploader(
    "2. Faça o upload da planilha de NOMES e CPFs (.xlsx)",
    type="xlsx"
)

# --- 2.2. Lógica de Processamento ---
# O código abaixo só roda se os DOIS arquivos tiverem sido enviados
if file_cobrancas is not None and file_cpfs is not None:
