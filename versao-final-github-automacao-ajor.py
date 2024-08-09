import datetime
from datetime import datetime, timedelta
import time
import requests
import json
import smtplib
from email.message import Message
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def conectar_com_gsheets(arquivo_json):
    """
    Realiza a conexão com Google Sheets a partir de um arquivo `json`
    de credenciais de conta de serviço.
    """
    escopo = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credenciais = ServiceAccountCredentials.from_json_keyfile_name(arquivo_json, escopo)
    return gspread.authorize(credenciais)


def ler_planilha(id, arquivo_json):
    """
    Lê uma planilha do Google Sheets a partir de seu ID e retorna um
    dataframe de Pandas com as informações.
    """
    cliente = conectar_com_gsheets(arquivo_json)
    planilha = cliente.open_by_key(id)
    dados = planilha.sheet1.get_all_records()
    return pd.DataFrame(dados)


def formatar_dados(df):
    """
    Formata data e retorn lista de dicionários.
    """
    lista_dicts = df.to_dict(orient='records')
    for i in lista_dicts:
        if i['DATA'] == '':
            i['DATA'] = None
        else:
            i['DATA'] = time.strftime('%d/%m/%Y', time.gmtime(i['DATA']))

    hoje = datetime.today().date()
    listagem = []
    for i in lista_dicts:
        try:
            data_insercao = datetime.strptime(i['DATA'], '%d/%m/%Y').date()
        except TypeError:
            data_insercao = None

        if data_insercao == hoje:
            listagem.append(
                {
                    'cnpj': i['CNPJ'].replace('/', '').replace('-', '').replace('.', ''),
                    'email': i['EMAIL'],
                    'sobre': i['QUEM SOMOS'],
                    'data': i['DATA'],
                    'nome_empresa': i['NOME'],
                }
            )
    return listagem


def configurar_email(destinatario, assunto, corpo_email):
    """
    Função genérica com configurações para enviar email.
    """
    msg = Message()
    msg['Subject'] = "Pedido de Associação à Ajor"
    msg['From'] = 'faleconosco@ajor.org.br'
    msg['To'] = destinatario
    password = ''  # Senha do email
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


def enviar_email(destinatario, nome_empresa):
    """
    Dispara um email quando a associação cumpre todos os pré-requisitos.
    """
    corpo_email = f"""
    <p>Olá {nome_empresa}</p>
    <p>Espero que esteja bem!</p>
    <p>Depois de uma avaliação preliminar positiva dos dados enviados por você, pelo site da Associação de Jornalismo Digital (Ajor),
    solicitando a associação de sua organização de mídia à Ajor, comunico que seu pedido segue para a segunda fase de avaliação.</p>
    <p>Nesta segunda fase, você precisa preencher o formulário abaixo, fornecendo informações detalhadas sobre o funcionamento de sua organização,
    que será uma das principais fontes de informação para avaliação do Conselho Deliberativo e Executivo da Ajor sobre sua postulação.</p>
    <p> https://docs.google.com/forms/d/e/1FAIpQLSdfaU-pqzRdV3Tgt0AaO0brK7RNL219yJf7B1_M40blRJ8wCA/viewform</p>
    <p>Peço que responda ao formulário em até sete dias contados a partir de hoje.</p>
    <p>Qualquer dúvida, estou por aqui!</p>
    """

    configurar_email(
        destinatario, "Sobre o seu pedido de associação à Ajor - Fluxo 2", corpo_email
    )


def enviar_email_cnpj(destinatario, nome_empresa, cnpj):
    """
    Dispara um email quando o CNPJ da associação não está aberto há mais
    de um ano ou está inativo.
    """
    corpo_email = f"""
    <p>Olá {nome_empresa}</p>
    <p>Espero que esteja bem!</p>
    <p>A Associação de Jornalismo Digital (Ajor) tem alguns critérios iniciais para que organizações de mídia possam se tornar associadas (confira todos os detalhes aqui: https://ajor.org.br/associe-se/)</p>
    <p>Depois de uma primeira avaliação das informações preenchidas, constatou-se que o seu CNPJ não está ativo há mais de um ano ou não está ativo, de acordo com dados obtidos em https://receitaws.com.br/.
    Esse item é imprescindível para que a sua postulação à Ajor possa passar para a segunda fase. </p>
    <p>Se você considera isso um erro, por favor, entre em contato com o e-mail: gessika.costa@ajor.org.br.
    Caso não, o pedido  de associação poderá ser refeito quando o CNPJ completar, ao menos, 12 meses de registro  ou, de maneira alternativa, você pode comprovar a atividade regular da sua organização de mídia por no mínimo 24 meses.
    Para isso, basta enviar links de reportagens publicadas  no período referido para o e-mail gessika.costa@ajor.org.br </p>
    <p>Obrigada.</p>
    <p>Qualquer dúvida, estamos à disposição.</p>
    """
    configurar_email(
        destinatario,
        "Sobre o seu pedido de associação à Ajor (Tempo de CNPJ)",
        corpo_email,
    )


def enviar_email_expediente(destinatario, nome_empresa):
    """
    Dispara um email quando não são identificadas as palavras-chave
    pré-selecionadas na seção Expediente do site.
    """
    corpo_email = f"""
    <p>Olá {nome_empresa}</p>
    <p>Espero que esteja bem!</p>
    <p>A Associação de Jornalismo Digital (Ajor) tem alguns critérios iniciais para que organizações de mídia possam se tornar associadas (confira todos os detalhes aqui: https://ajor.org.br/associe-se/)</p>
    <p>A Ajor  considera que a transparência das informações é um dos indicadores de boas práticas do ambiente de jornalismo digital.</p>
    <p>Depois de uma primeira avaliação, constatou-se que a iniciativa não disponibiliza o “expediente/quem somos” no site.
    Esse item - assim como uma forma de contato válida disponível aos leitores - é imprescindível para que a sua postulação de associação  possa seguir para a segunda fase.</p>
    <p>Para darmos andamento ao pedido, solicitamos, por gentileza, que essas informações sejam publicadas no site.
    Quando isso for feito, por favor, nos indique para este e-mail: gessika.costa@ajor.org.br e o processo de associação será reiniciado.</p>
    <p>Se você considera isso um erro, nos contate pelo gessika.costa@ajor.org.br.</p>
    <p>Obrigada.</p>
    <p>Qualquer dúvida, estamos à disposição.</p>
    """
    configurar_email(
        destinatario,
        "Sobre o seu pedido de associação à Ajor (critérios de transparência)",
        corpo_email,
    )


def consultar_cnpj(cnpj):
    """
    Consulta a situação do CNPJ na API da ReceitaWS.
    """
    consulta = requests.get(f'https://receitaws.com.br/v1/cnpj/{cnpj}')
    return json.loads(consulta.text)


def calcular_tempo_cnpj(data_abertura):
    """
    Calcula o tempo de abertura do CNPJ.
    """
    hoje = datetime.today().date()
    diferenca = hoje - data_abertura.date()
    return diferenca


def checar_quemsomos(url):
    """
    Checa se as palavras-chave estão presentes no texto da URL.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone14,3; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/19A346 Safari/602.1'
    }
    palavras_chave = ['quem somos', 'expediente', 'equipe', 'publicação']
    segunda_consulta = requests.get(url, headers=headers)
    if segunda_consulta.status_code == 200:
        info = segunda_consulta.text
        conteudo = info.lower()
        palavras_encontradas = [
            palavra.lower() in conteudo for palavra in palavras_chave
        ]
        return len(palavras_encontradas) >= 1
    return False


if __name__ == '__main__':
    planilha = ''  # ID da planilha
    arquivo_json = ''  # Arquivo de credenciais do Google Sheets
    df = ler_planilha(planilha, arquivo_json)
    listagem = formatar_dados(df)

    for e, c in enumerate(listagem):
        if (
            e % 3 == 0 and e != 0
        ):  # API permite 3 consultas por minuto em sua versão gratuita
            time.sleep(62)
        dados = consultar_cnpj(c['cnpj'])
        if dados['situacao'] == 'ATIVA':
            data_abertura = datetime.strptime(dados['abertura'], '%d/%m/%Y')
            diferenca = calcular_tempo_cnpj(data_abertura)
            if diferenca > timedelta(days=365):
                print(f'{c["cnpj"]}: Aberto há mais de um ano')
                quemsomos = checar_quemsomos(c['sobre'])
                if quemsomos:
                    print(f'{c["cnpj"]}: Ao menos uma palavra-chave foi encontrada')
                    enviar_email(c['email'], c['nome_empresa'])
                else:
                    print('Nenhuma palavra-chave foi encontrada')
                    enviar_email_expediente(c['email'], c['nome_empresa'])
            else:
                print(f'{c["cnpj"]}: Aberto há menos de um ano')
                enviar_email_cnpj(c['email'], c['nome_empresa'], c['cnpj'])
        else:
            print(f'{c["cnpj"]}: CNPJ não está ativo')
            enviar_email_cnpj(c['email'], c['nome_empresa'], c['cnpj'])
