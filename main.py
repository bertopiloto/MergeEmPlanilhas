import streamlit as st
import pandas as pd

# Definir o número máximo de planilhas que podem ser carregadas
MAX_PLANILHAS = 10

st.title("Aplicação de Merge de Planilhas")

# Escolher a quantidade de planilhas
quantidade_planilhas = st.number_input(
    "Quantas planilhas deseja carregar?", min_value=1, max_value=MAX_PLANILHAS, step=1
)

# Carregar as planilhas
arquivos = []
for i in range(quantidade_planilhas):
    arquivo = st.file_uploader(f"Carregar planilha {i+1}", type=["csv", "xlsx"])
    if arquivo:
        arquivos.append(pd.read_csv(arquivo) if arquivo.name.endswith(".csv") else pd.read_excel(arquivo))

# Continuar se houver arquivos carregados
if len(arquivos) > 0:
    # Selecionar a planilha principal
    nomes_arquivos = [f"Planilha {i+1}" for i in range(len(arquivos))]
    planilha_principal_idx = st.selectbox("Escolha sua planilha principal:", range(len(arquivos)), format_func=lambda x: nomes_arquivos[x])
    planilha_principal = arquivos[planilha_principal_idx]

    # Selecionar a coluna-chave (slabe) da planilha principal
    st.write("Selecione a coluna-chave da planilha principal:")
    chave_principal = st.selectbox("Coluna-chave da planilha principal:", planilha_principal.columns, key="chave_principal")

    # Escolher o tipo de merge
    tipo_merge = st.selectbox("Escolha o tipo de merge:", ["inner", "outer", "left", "right"])

    # Selecionar colunas equivalentes das outras planilhas
    colunas_merge = {}
    for i, planilha in enumerate(arquivos):
        if i != planilha_principal_idx:
            st.write(f"Selecione a coluna da {nomes_arquivos[i]} que corresponde à chave principal:")
            colunas_merge[i] = st.selectbox(f"Coluna da {nomes_arquivos[i]}:", planilha.columns, key=f"coluna_{i}")

    # Selecionar colunas adicionais que deseja importar
    colunas_adicionais = {}
    for i, planilha in enumerate(arquivos):
        if i != planilha_principal_idx:
            st.write(f"Selecione as colunas da {nomes_arquivos[i]} que deseja adicionar ao merge:")
            colunas_adicionais[i] = st.multiselect(f"Colunas da {nomes_arquivos[i]}:", planilha.columns, key=f"colunas_adicionais_{i}")

    # Botão para executar o merge
    if st.button("Executar Merge"):
        resultado = planilha_principal.copy()  # Garantir que a planilha principal não seja alterada

        # Realizar o merge com as colunas escolhidas
        for i, planilha in enumerate(arquivos):
            if i != planilha_principal_idx:
                # Filtrar apenas as colunas selecionadas
                cols_para_merge = [colunas_merge[i]] + colunas_adicionais[i]
                temp_planilha = planilha[cols_para_merge]

                # Realizar o merge
                resultado = resultado.merge(
                    temp_planilha,
                    how=tipo_merge,
                    left_on=chave_principal,
                    right_on=colunas_merge[i],
                    suffixes=("", f"_{nomes_arquivos[i]}"),
                )

        # Mostrar o resultado
        st.write("Resultado do Merge:")
        st.dataframe(resultado)

        # Botão para download
        csv = resultado.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar Resultado", data=csv, file_name="resultado_merge.csv", mime="text/csv")
