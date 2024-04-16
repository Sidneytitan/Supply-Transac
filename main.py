import streamlit as st

# Adicionando um emoji ao título da página
st.set_page_config(page_title="🚀Sidney Ribeiro")

def app():  # Corrigido: adicionando a palavra-chave "def"
    # Exibir a imagem da logo com o texto na mesma linha
    logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
    logo_size = (150, 40)  # Tamanho da imagem (largura, altura)

    # Coloque a imagem e o texto em uma linha
    st.image(logo_path, width=logo_size[0])
    st.header('Sidney Ribeiro de Oliveira', divider='rainbow')

app()





