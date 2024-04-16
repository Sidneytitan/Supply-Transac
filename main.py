import streamlit as st

# Adicionando um emoji ao título da página
st.set_page_config(page_title="🚀Sidney Ribeiro")

def app():  # Corrigido: adicionando a palavra-chave "def"
    # Exibir a imagem da logo com o texto na mesma linha
    logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
    logo_size = (150, 40)  # Tamanho da imagem (largura, altura)

    # Coloque a imagem e o texto em uma linha
    st.image(logo_path, width=logo_size[0])
    st.header('Supply Chain', divider='rainbow')

    # Adicionando o texto sobre a importância do controle de estoque
    st.write("""
    **A Importância de um Sistema para Controlar a Entrada e Saída no Estoque**

    Gerenciar eficientemente a entrada e saída de produtos no estoque é essencial para o sucesso de qualquer negócio, especialmente em setores como o da cadeia de suprimentos. Um sistema robusto de controle de estoque desempenha um papel fundamental na otimização das operações, garantindo que a empresa possa atender às demandas dos clientes de maneira oportuna, enquanto minimiza custos e maximiza lucros.

    Um dos benefícios mais significativos de um sistema de controle de estoque é a capacidade de acompanhar de perto o fluxo de mercadorias dentro e fora do armazém. Isso permite uma visão clara dos níveis de estoque em tempo real, evitando tanto a escassez quanto o excesso de produtos. Com essa visibilidade, as empresas podem tomar decisões informadas sobre compras, produção e distribuição, garantindo uma gestão mais eficaz dos recursos.

    Além disso, um sistema de controle de estoque automatizado pode ajudar a reduzir erros humanos e melhorar a precisão dos registros. Ao usar tecnologias como códigos de barras, RFID (Identificação por Radiofrequência) e sistemas de gestão de inventário, as empresas podem rastrear cada item individualmente, desde sua entrada no estoque até sua saída para o cliente final. Isso não apenas aumenta a eficiência operacional, mas também fortalece a confiança do cliente, garantindo que os pedidos sejam entregues corretamente e no prazo.

    Outro aspecto crucial é a capacidade de prever demandas futuras com base em dados históricos e tendências de mercado. Um sistema de controle de estoque bem projetado pode fornecer insights valiosos sobre padrões de compra e sazonalidade, permitindo que as empresas antecipem e se adaptem às mudanças nas necessidades do mercado.

    Em resumo, investir em um sistema eficiente para controlar a entrada e saída no estoque não é apenas uma medida preventiva, mas uma estratégia fundamental para o sucesso a longo prazo de qualquer negócio. Ao garantir uma gestão transparente e precisa dos recursos, as empresas podem melhorar sua competitividade, satisfação do cliente e rentabilidade.
    """)

app()






