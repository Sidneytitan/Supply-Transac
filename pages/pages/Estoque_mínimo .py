import streamlit as st
from pymongo import MongoClient
import pandas as pd


# Função para conectar ao banco de dados MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/?retryWrites=true&w=majority")
    db = client["titan"]
    return db


# Função para atualizar as quantidades mínimas desejadas no banco de dados
def atualizar_estoque_minimo(quantidades_minimas):
    db = connect_to_mongodb()
    collection = db["EstoqueMinimo"]
    collection.drop()  # Limpa a coleção antes de inserir os novos documentos
    for produto, quantidade in quantidades_minimas.items():
        collection.insert_one({"nome_produto": produto, "quantidade_minima": quantidade})


# Função para carregar as quantidades mínimas desejadas do banco de dados
def carregar_estoque_minimo():
    db = connect_to_mongodb()
    collection = db["EstoqueMinimo"]
    quantidades_minimas = {}
    for document in collection.find({}):
        quantidades_minimas[document["nome_produto"]] = document["quantidade_minima"]
    return quantidades_minimas


# Função para calcular a quantidade total de cada produto no estoque
def calcular_quantidade_total_por_produto(filiais):
    db = connect_to_mongodb()
    collection = db["estoque"]

    # Adiciona a opção "Todas as Filiais" no início da lista
    filiais.insert(0, "Todas as Filiais")

    # Adiciona um filtro por filial na barra lateral
    filtro_filial = st.sidebar.selectbox("Filtrar por Filial", filiais)

    # Define o filtro de acordo com a filial selecionada
    filtro = {} if filtro_filial == "Todas as Filiais" else {"filial": filtro_filial}

    movimentacoes_df = pd.DataFrame(list(collection.find(filtro, {"_id": 0})))

    # Verifica se há dados no DataFrame
    if movimentacoes_df.empty or movimentacoes_df["data_movimento"].isnull().all():
        return pd.DataFrame(columns=["Nome do Produto", "Quantidade Total"])

    # Agrupa as movimentações por nome do produto e calcula a quantidade total
    quantidade_total_por_produto = movimentacoes_df.groupby("nome_produto")["quantidade_movimento"].sum().reset_index()
    quantidade_total_por_produto.rename(
        columns={"nome_produto": "Nome do Produto", "quantidade_movimento": "Quantidade Total"}, inplace=True)

    return quantidade_total_por_produto


def main():
    # Configuração da página
    st.set_page_config(page_title="🚀 Sidney Ribeiro", layout="wide")

    # Título da página
    logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
    logo_size = (150, 40)  # Tamanho da imagem (largura, altura)
    st.image(logo_path, width=logo_size[0])
    st.header('Quantidade de Cada Produto no Estoque', divider='rainbow')

    # Obtém a lista de filiais da coleção "estoque"
    db = connect_to_mongodb()
    collection = db["estoque"]
    filiais = collection.distinct("filial")

    # Adiciona a segunda aba para definir a quantidade desejada para cada produto
    opcao_menu = st.sidebar.selectbox("Selecione uma opção", ["Visualizar Estoque", "Definir Quantidade Desejada"])

    if opcao_menu == "Visualizar Estoque":
        # Adiciona a tabela de quantidade de cada produto no estoque
        quantidade_total_por_produto = calcular_quantidade_total_por_produto(filiais)

        # Carrega as quantidades mínimas desejadas do banco de dados
        quantidades_minimas = carregar_estoque_minimo()

        # Verifica se a quantidade total no estoque é menor ou igual à quantidade mínima desejada para cada produto
        # Se for o caso, aplica um estilo para destacar essa linha na tabela
        def highlight_row(row):
            produto = row["Nome do Produto"]
            quantidade_total = row["Quantidade Total"]
            if produto in quantidades_minimas and quantidade_total <= quantidades_minimas[produto]:
                return ['background-color: #FF4869'] * len(row)
            else:
                return [''] * len(row)

        st.dataframe(quantidade_total_por_produto.style.apply(highlight_row, axis=1))

    elif opcao_menu == "Definir Quantidade Desejada":
        # Título da aba
        st.subheader("Definir Quantidade Desejada para Cada Produto")

        # Obtém a lista de produtos
        produtos = calcular_quantidade_total_por_produto(filiais)["Nome do Produto"].tolist()

        # Carrega as quantidades mínimas desejadas do banco de dados
        quantidades_minimas = carregar_estoque_minimo()

        # Cria um dicionário para armazenar as quantidades desejadas para cada produto
        quantidades_desejadas = {}

        # Para cada produto, adicionar um campo de entrada de texto para que o usuário possa digitar a quantidade desejada
        for produto in produtos:
            valor_atual = quantidades_minimas.get(produto, 0)
            quantidades_desejadas[produto] = st.text_input(f"Quantidade desejada para {produto}", value=valor_atual)

        # Atualizar as quantidades mínimas desejadas no banco de dados ao clicar em um botão
        if st.button("Salvar Quantidades Desejadas"):
            st.success('Estoque minimo cadastrado com sucesso!')
            quantidades_desejadas_numerico = {produto: int(quantidade) for produto, quantidade in
                                              quantidades_desejadas.items()}
            atualizar_estoque_minimo(quantidades_desejadas_numerico)


if __name__ == '__main__':
    main()







