import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Função para conectar ao banco de dados MongoDB
def connect_to_mongodb():
    client = MongoClient("mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/?retryWrites=true&w=majority")
    db = client["titan"]
    collection = db["estoque"]  # Coleção para os produtos cadastrados
    return collection

# Função para adicionar uma nova movimentação ao estoque
def add_movimentacao_to_estoque(movimentacao):
    collection = connect_to_mongodb()

    # Se a movimentação for do tipo "Entrada", define "Não aplicável" para quem_lancou e quem_retirou
    if movimentacao["tipo_movimentacao"] == "Entrada":
        movimentacao["quem_lancou"] = "Não aplicável"
        movimentacao["quem_retirou"] = "Não aplicável"

    collection.insert_one(movimentacao)

# Função para recuperar os produtos cadastrados na coleção lista_produtos
def get_lista_produtos():
    client = MongoClient("mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/?retryWrites=true&w=majority")
    db = client["titan"]
    collection = db["lista_produtos"]  # Coleção para os produtos cadastrados
    produtos = list(collection.find({}, {"_id": 0}))  # Excluir o campo _id
    return produtos

# Função para exibir as movimentações cadastradas no estoque
def display_movimentacoes(filtro_produto):
    collection = connect_to_mongodb()
    movimentacoes_df = pd.DataFrame(list(collection.find({}, {"_id": 0})))

    # Verifica se há dados no DataFrame
    if movimentacoes_df.empty or movimentacoes_df["data_movimento"].isnull().all():
        st.warning("Não há movimentações no estoque ou as datas das movimentações não são válidas.")
        return

    # Converte as datas para o tipo datetime
    movimentacoes_df["data_movimento"] = pd.to_datetime(movimentacoes_df["data_movimento"], format="%d/%m/%Y")

    # Calcula o valor mínimo e máximo da data
    min_data = movimentacoes_df["data_movimento"].min()
    max_data = movimentacoes_df["data_movimento"].max()

    # Verifica se o máximo valor de data é válido
    if pd.isnull(min_data) or pd.isnull(max_data):
        st.warning("As datas das movimentações não são válidas.")
        return

    # Dividindo a tela em duas colunas
    col1, col2 = st.columns(2)

    # Primeira coluna para o input de data inicial
    with col1:
        data_inicio = st.date_input("**Filtrar por data inicial**",
                                    min_value=min_data,
                                    max_value=max_data,
                                    value=min_data,
                                    format="DD/MM/YYYY")  # Definindo o formato para dd/mm/yyyy

    # Segunda coluna para o input de data final
    with col2:
        data_fim = st.date_input("**Filtrar por data final**",
                                 min_value=min_data,
                                 max_value=max_data,
                                 value=max_data,
                                 format="DD/MM/YYYY")  # Definindo o formato para dd/mm/yyyy

    # Aplica o filtro de data
    movimentacoes_filtradas = movimentacoes_df[
        (movimentacoes_df["data_movimento"] >= pd.Timestamp(data_inicio)) &
        (movimentacoes_df["data_movimento"] <= pd.Timestamp(data_fim))]

    # Aplica o filtro de produto
    if filtro_produto:
        movimentacoes_filtradas = movimentacoes_filtradas[
            movimentacoes_filtradas["nome_produto"].str.contains(filtro_produto)]

    # Adiciona a coluna de valor unitário
    movimentacoes_filtradas['valor_unitario'] = movimentacoes_filtradas['valor_pago'] / movimentacoes_filtradas[
        'quantidade_movimento']

    # Agrupa as movimentações por tipo de movimentação e data
    movimentacoes_agrupadas = movimentacoes_filtradas.groupby(
        ["data_movimento", "tipo_movimentacao"]).sum().reset_index()

    # Calcula o estoque final
    entradas = movimentacoes_agrupadas[movimentacoes_agrupadas["tipo_movimentacao"] == "Entrada"][
        "quantidade_movimento"].sum()
    saidas = movimentacoes_agrupadas[movimentacoes_agrupadas["tipo_movimentacao"] == "Saída"][
        "quantidade_movimento"].sum()
    estoque_final = entradas + saidas

    # Calcula o total do valor pago
    total_valor_pago = movimentacoes_filtradas["valor_pago"].sum()

    # Cria os cartões para mostrar as somas
    st.subheader("Resumo de Movimentações")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col1:
        st.metric(label="**Total de Entradas**", value=entradas)
    with col2:
        st.metric(label="**Total de Saídas**", value=saidas)
    with col3:
        st.metric(label="**Estoque Final**", value=estoque_final)
    with col4:
        st.metric(label="**Total Valor Pago**", value=total_valor_pago)

    st.subheader('Movimentações no Estoque')

    # Verifica se há movimentações para o intervalo de datas selecionado
    if not movimentacoes_filtradas.empty:
        st.dataframe(movimentacoes_filtradas)

        # Cria um gráfico de barras para mostrar as quantidades movimentadas por tipo de movimentação e data
        fig_bar = go.Figure()

        for tipo in movimentacoes_agrupadas["tipo_movimentacao"].unique():
            data_tipo = movimentacoes_agrupadas[movimentacoes_agrupadas["tipo_movimentacao"] == tipo]
            fig_bar.add_trace(go.Bar(
                x=data_tipo["data_movimento"],
                y=data_tipo["quantidade_movimento"],
                name=tipo,
                marker_color='#164888' if tipo == 'Entrada' else '#EF4824',
                text=data_tipo["quantidade_movimento"],
                textposition='auto'
            ))

        fig_bar.update_layout(
            title='Quantidade Movimentada por Tipo de Movimentação e Data',
            xaxis_title='Data da Movimentação',
            yaxis_title='Quantidade Movimentada',
            barmode='group',
            hovermode="x unified"
        )

        st.plotly_chart(fig_bar)

        # Cria um gráfico de linha comparativo para mostrar as entradas e saídas ao longo do tempo
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Entrada']['data_movimento'],
            y=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Entrada'][
                'quantidade_movimento'],
            mode='lines+markers',
            name='Entradas',
            line=dict(color='#164888'),
            text=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Entrada'][
                'quantidade_movimento']))

        fig.add_trace(go.Scatter(
            x=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Saída']['data_movimento'],
            y=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Saída']['quantidade_movimento'],
            mode='lines+markers',
            name='Saídas',
            line=dict(color='#EF4824'),
            text=movimentacoes_filtradas[movimentacoes_filtradas['tipo_movimentacao'] == 'Saída'][
                'quantidade_movimento']))

        fig.update_layout(title='Movimentações no Estoque ao Longo do Tempo',
                          xaxis_title='Data da Movimentação',
                          yaxis_title='Quantidade Movimentada',
                          hovermode="x unified")

        st.plotly_chart(fig)

    else:
        st.warning("Não há movimentações para o intervalo de datas e produto selecionados.")

    # Exibir o valor unitário no MongoDB
    for index, movimentacao in movimentacoes_filtradas.iterrows():
        # Obtém o valor unitário da linha
        valor_unitario = movimentacao['valor_unitario']
        # Atualiza o documento no MongoDB com o valor unitário
        collection.update_one({"_id": index}, {"$set": {"valor_unitario": valor_unitario}})

# Função para obter o último valor de entrada para um produto específico
def get_ultimo_valor_entrada(id_produto):
    collection = connect_to_mongodb()
    # Encontrar a entrada mais recente para o produto selecionado
    ultima_entrada = collection.find_one({"id_produto": id_produto, "tipo_movimentacao": "Entrada"},
                                          sort=[("data_movimento", 1)])
    # Verificar se foi encontrada uma entrada
    if ultima_entrada:
        # Retornar o valor unitário da última entrada
        return ultima_entrada.get("valor_unitario", 0.0)
    # Se não houver entrada encontrada, retornar 0.0
    return 0.0









# Função para recuperar as opções de "Recebido por" do banco de dados MongoDB
def get_quem_retirou_options():
    client = MongoClient("mongodb+srv://sidneycko:titanbetty@cluster0.feenv6t.mongodb.net/?retryWrites=true&w=majority")
    db = client["titan"]
    collection = db["Recebido por"]  # Coleção para as opções de "Recebido por"
    options = [option.get("valor", "") for option in collection.find({}, {"_id": 0})]

    return options


# Função para obter os nomes dos produtos
def get_nomes_produtos(produtos):
    return [produto.get('nome') for produto in produtos]

def main():
    # Configuração da página
    st.set_page_config(page_title="🚀 Sidney Ribeiro", layout="wide")

    # Sidebar
    st.sidebar.title("Menu")

    # Usando botões de alternância para uma aparência mais moderna
    opcao_menu = st.sidebar.selectbox("**Selecione uma opção**", ["Cadastrar Movimentação", "Visualizar Movimentações"])

    if opcao_menu == "Cadastrar Movimentação":
        # Título da página
        logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
        logo_size = (150, 40)  # Tamanho da imagem (largura, altura)
        st.image(logo_path, width=logo_size[0])
        st.header('Nova Movimentação no Estoque', divider='rainbow')

        # Conecta ao MongoDB e carrega os produtos cadastrados
        produtos = get_lista_produtos()

        # Obtém os nomes dos produtos
        nomes_produtos = get_nomes_produtos(produtos)

        # Formulário para cadastro de movimentações no estoque
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            nome_produto = st.selectbox('**Nome do Produto**', options=nomes_produtos)
            # Obtém o ID do produto selecionado
            id_produto = next((produto.get('id') for produto in produtos if produto.get('nome') == nome_produto), None)
            # Busca a categoria correspondente ao produto selecionado
            categoria_produto = next((produto.get('categoria') for produto in produtos if produto.get('nome') == nome_produto),
                                     None)
            st.write(f'**Categoria do Produto:** {categoria_produto}')
        with col2:
            st.text_input('**ID do Produto**', value=id_produto, key='id_produto')
        with col3:
            tipo_movimentacao = st.radio('**Tipo de Movimentação**', ['Entrada', 'Saída'])
        with col4:
            quantidade_movimentacao = st.number_input('**Quantidade Movimentada**', min_value=1, step=1)

        # Adicione uma linha em branco
        st.write("")

        # Adicione os campos na linha abaixo
        col5, col6, col7 = st.columns([2, 1, 1])
        with col5:
            if tipo_movimentacao == "Entrada":
                valor_unitario = st.number_input('**Valor Unitário (R$)**', min_value=0.0, step=0.01)
            else:
                # Preenche automaticamente o valor unitário com o último valor de entrada para o produto selecionado
                ultimo_valor_entrada = get_ultimo_valor_entrada(id_produto)
                valor_unitario = st.number_input('**Valor Unitário (R$)**', value=ultimo_valor_entrada, min_value=0.0, step=0.01)
        with col6:
            total_valor_pago = quantidade_movimentacao * valor_unitario
            st.write('**Total Valor Pago (R$)**')
            st.write(f'**{total_valor_pago:.2f}**')

        with col7:
            data_movimento = st.date_input('**Data da Movimentação**', format="DD/MM/YYYY")

        # Os campos restantes permanecem na linha seguinte
        filial = st.selectbox('**Filial**', ['Paulínia', 'Uberlândia', 'Barueri'])

        # Define os valores padrão para "Recebido por" e "Entregador"
        recebido_por_value = "Não aplicável" if tipo_movimentacao == "Entrada" else None
        entregador_value = "Não aplicável" if tipo_movimentacao == "Entrada" else None

        # Obter as opções de "Recebido por" do banco de dados
        quem_retirou_options = get_quem_retirou_options()
        quem_retirou = st.selectbox('**Entregue para**', options=quem_retirou_options, index=0 if tipo_movimentacao == "Entrada" else None,
                                    key="recebido_por", format_func=lambda x: "Não aplicável" if tipo_movimentacao == "Entrada" else x)

        quem_lancou_options = ["NICOLAS GOMES DA FONSECA", "LEONARDO REZENDE DINIZ", "SIDNEY RIBEIRO DE OLIVEIRA"]
        quem_lancou = st.selectbox('**Entregador**', options=quem_lancou_options, index=0 if tipo_movimentacao == "Entrada" else None,
                                   key="entregador", format_func=lambda x: "Não aplicável" if tipo_movimentacao == "Entrada" else x)

        observacao = st.text_area('**Observações**', height=100)

        if st.button('Adicionar Movimentação'):
            # Define a quantidade de movimento como positiva para entradas e negativa para saídas
            quantidade_movimentacao = quantidade_movimentacao if tipo_movimentacao == 'Entrada' else -quantidade_movimentacao
            # Monta o documento da movimentação
            movimentacao = {
                "id_produto": id_produto,
                "nome_produto": nome_produto,
                "quantidade_movimento": quantidade_movimentacao,
                "data_movimento": data_movimento.strftime("%d/%m/%Y"),
                "tipo_movimentacao": tipo_movimentacao,
                "filial": filial,
                "valor_pago": quantidade_movimentacao * valor_unitario,
                "valor_unitario": valor_unitario,
                "quem_lancou": quem_lancou,
                "quem_retirou": quem_retirou,
                "observacao": observacao
            }
            # Adiciona a movimentação ao estoque
            add_movimentacao_to_estoque(movimentacao)
            st.success('Movimentação cadastrada com sucesso!')

    elif opcao_menu == "Visualizar Movimentações":
        # Título da página
        logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
        logo_size = (150, 40)  # Tamanho da imagem (largura, altura)
        st.image(logo_path, width=logo_size[0])
        st.header('Visualizar Movimentações no Estoque', divider='rainbow')

        # Adiciona a barra de pesquisa para filtrar por produto na sidebar
        filtro_produto = st.sidebar.text_input("**Pesquisar Produto**", key="pesquisar_produto")
        display_movimentacoes(filtro_produto)

if __name__ == '__main__':
    main()








