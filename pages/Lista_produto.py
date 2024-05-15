import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Função para conectar ao banco de dados MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/?retryWrites=true&w=majority")
    db = client["titan"]
    collection = db["lista_produtos"] # Coleção para os produtos cadastrados
    return collection

# Função para recuperar os produtos cadastrados na coleção lista_produtos
def get_lista_produtos():
    collection = connect_to_mongodb()
    produtos = list(collection.find({}, {'_id': 0}))  # Excluindo o campo _id
    return produtos

def cadastrar_produto_mongodb(produto):
    collection = connect_to_mongodb()
    collection.insert_one(produto)

def cadastrar_produto_page():
    st.title('Cadastro de Produtos')

    id_produto = st.number_input('**ID do Produto**', min_value=1, step=1)
    nome_produto = st.text_input('**Nome do Produto**')
    categoria_produto = st.selectbox('**Categoria do Produto**', ['EPI', 'EPC', 'PEÇA', 'UNIFORME'])

    if st.button('Cadastrar Produto'):
        produto = {
            "id": id_produto,
            "nome": nome_produto,
            "categoria": categoria_produto
        }
        cadastrar_produto_mongodb(produto)
        st.success('Produto cadastrado com sucesso!')

def visualizar_produtos_cadastrados():
    st.title('Produtos Cadastrados')

    produtos = get_lista_produtos()
    if produtos:
        # Adicionando o último produto cadastrado à lista de produtos na posição correta
        ultimo_cadastro = produtos[-1]
        produtos.pop()  # Remover o último cadastro da lista original
        produtos.append(ultimo_cadastro)  # Adicionar o último cadastro no final da lista

        df = pd.DataFrame(produtos)
        st.dataframe(df.style.set_properties(**{'text-align': 'center'}))  # Usando st.dataframe() para uma exibição mais bonita
    else:
        st.write('Nenhum produto cadastrado ainda.')

def main():
    st.sidebar.title('Menu')
    selected_page = st.sidebar.radio('Selecione uma opção', ['Cadastro de Produtos', 'Visualizar Produtos'])

    if selected_page == 'Cadastro de Produtos':
        cadastrar_produto_page()
    elif selected_page == 'Visualizar Produtos':
        visualizar_produtos_cadastrados()

if __name__ == '__main__':
    main()


