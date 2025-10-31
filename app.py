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
        ('background-color', '#8DB4E2'), # Novo azul do cabeçalho
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
st.write("Esta aplicação cruza a planilha de cobranças com a de CPFs.")

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
    
    # Bloco 'try...except' para capturar erros (ex: nomes de colunas errados)
    try:
        # Mostra uma mensagem de "carregando" enquanto processa
        with st.spinner("Processando arquivos... Por favor, aguarde."):
            
            # --- Ler os arquivos ---
            df_cobrancas = pd.read_excel(file_cobrancas)
            df_cpfs = pd.read_excel(file_cpfs)

            # --- Validar, converter e limpar CPFs ---
            if 'CPF' not in df_cpfs.columns or 'PESSOA' not in df_cpfs.columns:
                st.error("ERRO: A planilha de Nomes-CPFs precisa ter as colunas 'PESSOA' e 'CPF'.")
                st.stop() # Para a execução

            df_cpfs['CPF'] = df_cpfs['CPF'].astype(str)
            
            contagem_antes = len(df_cpfs)
            df_cpfs = df_cpfs.drop_duplicates(subset=['CPF'], keep='first')
            contagem_depois = len(df_cpfs)
            removidos = contagem_antes - contagem_depois

            if removidos > 0:
                st.success(f"Sucesso: Foram removidos {removidos} registros com CPF duplicado.")
            else:
                st.info("Nenhum CPF duplicado foi encontrado.")

            # --- Cruzar dados e Reorganizar ---
            if 'ALUNO' not in df_cobrancas.columns:
                st.error("ERRO: A planilha de Cobranças precisa ter a coluna 'ALUNO'.")
                st.stop() # Para a execução
            
            df_final = pd.merge(df_cobrancas, df_cpfs, left_on='ALUNO', right_on='PESSOA', how='left')

            if 'PESSOA' in df_final.columns:
                df_final = df_final.drop(columns=['PESSOA'])

            colunas_atuais = list(df_final.columns)
            colunas_atuais.remove('CPF')
            posicao_aluno = colunas_atuais.index('ALUNO')
            colunas_reordenadas = colunas_atuais[:posicao_aluno+1] + ['CPF'] + colunas_atuais[posicao_aluno+1:]
            df_final = df_final[colunas_reordenadas]

            # --- Aplicar Estilos ---
            df_estilizado = df_final.style \
                .apply(zebra_stripes, axis=1) \
                .map(destacar_vazios, subset=['CPF']) \
                .set_table_styles([header_style])
            
            st.success("Planilha processada e formatada com sucesso!")

            # --- 2.3. Preparar o arquivo para Download ---
            
            # Salva o arquivo Excel estilizado em um buffer de memória
            output_buffer = io.BytesIO()
            df_estilizado.to_excel(output_buffer, index=False, engine='openpyxl')
            
            st.download_button(
                label="Clique aqui para baixar a planilha final (.xlsx)",
                data=output_buffer,
                file_name="Contas_com_CPF.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante o processamento: {e}")
        st.warning("Verifique se os arquivos são os corretos e se os nomes das colunas ('ALUNO', 'PESSOA', 'CPF') estão exatos.")
