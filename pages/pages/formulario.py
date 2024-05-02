import streamlit as st
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
from reportlab.lib.utils import ImageReader

# Função para gerar PDF
def generate_pdf(driver_list, monitor_name, font_size, filial, operacao, periodo_infra,
                 num_pedido, razao_social, cnpj_fornecedor, forma_pagamento, valor,
                 banco, agencia, conta, motivo, observacao):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as buffer:
        cnv = canvas.Canvas(buffer.name, pagesize=A4)
        cnv.setFontSize(font_size)

        # Desenha o cabeçalho
        x_start = 50
        y = 700  # Posição vertical inicial do cabeçalho

        # Adiciona informações da filial, operação e período de infrações ao cabeçalho
        if filial or operacao or periodo_infra:
            x_filial = 100  # Posição X inicial da filial
            x_operacao = 250  # Posição X inicial da operação
            x_periodo_infra = 400  # Posição X inicial do período de infrações
            y_header = y  # Posição Y do cabeçalho

            header_info = ""
            if filial:
                header_info += f"Filial: {filial} "
            if operacao:
                header_info += f"Operação: {operacao} "
            if periodo_infra:
                periodo_infra_str = f"{periodo_infra[0].strftime('%d/%m/%Y')} - {periodo_infra[1].strftime('%d/%m/%Y')}"
                header_info += f"Período de Infrações: {periodo_infra_str}"

            # Desenha as informações do cabeçalho
            cnv.setFont("Helvetica-Bold", font_size)  # Define a fonte como negrito
            cnv.drawString(x_filial, y_header, "FILIAL")
            cnv.drawString(x_operacao, y_header, "OPERAÇÃO")
            cnv.drawString(x_periodo_infra, y_header, "PERÍODO DE INFRAÇÕES")
            cnv.setFont("Helvetica", font_size)  # Retorna à fonte padrão

            # Desenha as entradas de filial, operação e período de infrações logo abaixo do cabeçalho
            y -= 1
            if filial or operacao or periodo_infra:
                x_input_filial = 100  # Posição X da entrada da filial
                x_input_operacao = 250  # Posição X da entrada da operação
                x_input_periodo_infra = 400  # Posição X da entrada do período de infrações
                input_info = ""
                if filial:
                    input_info += f"{filial} "
                if operacao:
                    input_info += f"{operacao} "
                if periodo_infra:
                    periodo_infra_str = f"{periodo_infra[0].strftime('%d/%m/%Y')} - {periodo_infra[1].strftime('%d/%m/%Y')}"
                    input_info += periodo_infra_str
                # Desenha as entradas
                cnv.drawString(x_input_filial, y - 20, filial)
                cnv.drawString(x_input_operacao, y - 20, operacao)
                cnv.drawString(x_input_periodo_infra, y - 20, periodo_infra_str)

        # Desenha os detalhes de cada motorista
        y -= 60  # Aumenta o espaço entre os inputs e o cabeçalho dos motoristas

        # Mostra os detalhes do motorista monitor
        if monitor_name:
            cnv.drawString(50, y - 90, f"Motorista Monitor: {monitor_name}")

        # Adiciona os detalhes do pedido
        if num_pedido or razao_social or cnpj_fornecedor or forma_pagamento or valor or banco or agencia or conta or motivo or observacao:
            cnv.setFont("Helvetica-Bold", font_size)  # Define a fonte como negrito
            y -= 50
            cnv.drawString(50, y - 110, "Detalhes do Pedido:")
            cnv.setFont("Helvetica", font_size)  # Retorna à fonte padrão
            y -= 30
            if num_pedido:
                cnv.drawString(50, y - 130, f"Número do Pedido: {num_pedido}")
            if razao_social:
                cnv.drawString(50, y - 150, f"Razão Social do Fornecedor: {razao_social}")
            if cnpj_fornecedor:
                cnv.drawString(50, y - 170, f"CNPJ do Fornecedor: {cnpj_fornecedor}")
            if forma_pagamento:
                cnv.drawString(50, y - 190, f"Forma de Pagamento: {forma_pagamento}")
            if valor:
                cnv.drawString(50, y - 210, f"Valor: {valor}")
            if banco:
                cnv.drawString(50, y - 230, f"Banco: {banco}")
            if agencia:
                cnv.drawString(50, y - 250, f"Agência: {agencia}")
            if conta:
                cnv.drawString(50, y - 270, f"Conta: {conta}")
            if motivo:
                cnv.drawString(50, y - 290, f"Motivo: {motivo}")
            if observacao:
                cnv.drawString(50, y - 310, f"Observação: {observacao}")

        cnv.save()

        buffer.seek(0)
        pdf = buffer.read()

    return pdf

def app():
    # Exibir a imagem da logo com o texto na mesma linha
    logo_path = "https://github.com/Sidneytitan/ayla/raw/main/Logo.png"
    logo_size = (150, 40)  # Tamanho da imagem (largura, altura)

    # Coloque a imagem e o texto em uma linha
    st.image(logo_path, width=logo_size[0])
    st.header('Segurança é um valor inegociável', divider='rainbow')

    st.sidebar.subheader("Opções")
    option = st.sidebar.radio("", ["Cadastro de Infrações"])

    if option == 'Cadastro de Infrações':
        # Cadastro de Motoristas e Geração de PDF
        st.title('CADASTRO DE INFRAÇÕES')

        # Cadastro de Filial, Operação e Período de Infrações
        st.subheader("Cadastre os detalhes da infração")
        col1, col2, col3 = st.columns(3)  # Divide em três colunas

        with col1:
            filial = st.text_input('Filial', value="Barueri")

        with col2:
            operacao = st.text_input('Operação', value="Distribuição")

        with col3:
            periodo_infra_input = st.text_input('Período', value="01/01/2022 - 31/12/2022")
            periodo_infra_parts = periodo_infra_input.split(" - ")
            if len(periodo_infra_parts) == 2:
                data_inicial = datetime.datetime.strptime(periodo_infra_parts[0], "%d/%m/%Y")
                data_final = datetime.datetime.strptime(periodo_infra_parts[1], "%d/%m/%Y")
                periodo_infra = (data_inicial, data_final)

        # Cadastro do Motorista Monitor
        st.subheader("Selecione o motorista monitor")
        monitor_name = st.selectbox('Nome do Motorista Monitor', ["SIDNEY RIBEIRO DE OLIVEIRA"])

        # Cadastro dos detalhes do pedido
        st.subheader("Detalhes do Pedido")
        col1, col2 = st.columns([1,1])
        with col1:
            num_pedido = st.text_input('Número do Pedido')
            razao_social = st.text_input('Razão Social do Fornecedor')
            cnpj_fornecedor = st.text_input('CNPJ do Fornecedor')
            forma_pagamento = st.text_input('Forma de Pagamento')
        with col2:
            valor = st.number_input('Valor', format="%.2f")
            banco = st.text_input('Banco', max_chars=3)
            agencia = st.text_input('Agência')
            conta = st.text_input('Conta')

        # Outros detalhes do pedido
        st.subheader("Outros Detalhes do Pedido")
        motivo = st.text_area('Motivo')
        observacao = st.text_area('Observação')

        # Botão para gerar PDF
        if st.button('Gerar PDF'):
            # Lista de motoristas para o exemplo
            driver_list = [
                {'ID': 1, 'Nome do Motorista': 'Motorista 1', 'CPF': '123456789', 'Infração': 'Sem EPI', 'Data': '01/01/2022', 'Horário': '10:00', 'Tipo de Contato': 'Telefone'},
                {'ID': 2, 'Nome do Motorista': 'Motorista 2', 'CPF': '987654321', 'Infração': 'Excesso veloc. PM', 'Data': '02/01/2022', 'Horário': '11:00', 'Tipo de Contato': 'E-mail'}
            ]

            # Gerar PDF
            pdf = generate_pdf(driver_list, monitor_name, 8, filial, operacao, periodo_infra,
                               num_pedido, razao_social, cnpj_fornecedor, forma_pagamento, valor,
                               banco, agencia, conta, motivo, observacao)

            # Botão para baixar PDF
            st.download_button(label="Baixar PDF", data=pdf, file_name="SIDNEY_pdf.pdf", mime="application/pdf")
            st.success("PDF gerado com sucesso!")

if __name__ == '__main__':
    app()
