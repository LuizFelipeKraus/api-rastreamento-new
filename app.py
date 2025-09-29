import traceback
import bleach
from dotenv import load_dotenv
from flask import Flask, request, render_template, make_response, jsonify
from db import get_db, get_db_alt, close_db


if load_dotenv():
    from src.application.factory.LoggerFactory import LoggerFactory
    from src.application.security.IpController import IpController
    from src.domain.ValidadorChave import ValidadorChave
    from src.infra.database.PostgresAdapter import PostgresAdapter
    from src.validarDadosRastreamento import validarRastreamento


def create_app():
    app = Flask(__name__)
    app.teardown_appcontext(close_db)
    app.url_map.strict_slashes = False
    return app


logger = LoggerFactory.create_logger('rastreamento', 'logs/rastreamento.log', terminal=False)
flask_logger = LoggerFactory.update_logger('werkzeug')
ip_controller = IpController(logger)
app = create_app()


@app.route('/rastreamento/status')
def status():
    try:
        conexao = get_db()

        if conexao.closed == 0:
            status = 'OK'
        else:
            status = "Conexão Perdida"

    except:
        status = "Erro ao conectar ao banco"

    return jsonify({"status": status})


@app.route('/rastreamento/v3/docs')
def docs():
    try:
        return render_template('index.html')

    except Exception as erro:
        logger.critical(str(erro))
        json_resposta = jsonify({'error': "Erro crítico na renderização da documentação"})
        response = make_response(json_resposta, 500)
        return response


@app.route('/rastreamento', methods=['POST'])
def rastreamento():
    try:
        dados_json = request.get_json(silent=True)

        if dados_json is None:
            return jsonify({"erro": "O corpo da requisição está vazio ou não é um JSON válido."}), 400

        conexao = get_db()
        conexao.autocommit = True
        adapter = PostgresAdapter(conexao, 'UTF8', logger)
        validador_chave = ValidadorChave(adapter)

        conexao_alfa = get_db_alt()
        conexao_alfa.autocommit = True
        adapter_alfa = PostgresAdapter(conexao_alfa, 'LATIN1', logger)

        ip_cliente = ip_controller.pegar_ip(request)
        chaveAcessoApi = dados_json.get('idr')
        chaveNotaFiscal = dados_json.get('merNF')
        cnpjTomador = dados_json.get('tomCnpj')
        modoJson = dados_json.get('modoJson')
        xmlCte = dados_json.get('xmlCte')

        chaveAcessoApi = bleach.clean(str(chaveAcessoApi)) if chaveAcessoApi else None
        chaveNotaFiscal = bleach.clean(str(chaveNotaFiscal)) if chaveNotaFiscal else None
        cnpjTomador = bleach.clean(str(cnpjTomador)) if cnpjTomador else None
        modoJson = bleach.clean(str(modoJson)) if modoJson else None
        xmlCte = bleach.clean(str(xmlCte)) if xmlCte else None

        if not chaveAcessoApi:
            return jsonify({"erro": "O campo 'idr' é obrigatório no JSON."}), 400

        logger.info(f"rastreamento - Chave Acesso: {chaveAcessoApi} | CNPJ: {cnpjTomador}")

        if ip_controller.verificar_bloqueio(ip_cliente):
            mensagem = f'Acesso bloqueado para o IP: {ip_cliente}, tente novamente mais tarde'
            logger.warning(mensagem)
            return make_response(jsonify({'error': mensagem}), 403)

        if not validador_chave.validar(chaveAcessoApi):
            ip_controller.nova_tentativa(ip_cliente)
            mensagem = 'chave de acesso incorreta'
            logger.warning(mensagem)
            return make_response(jsonify({'error': mensagem}), 403)

        dadosApi = {
            'chaveAcessoApi': chaveAcessoApi,
            'chaveNotaFiscal': chaveNotaFiscal,
            'cnpjTomador': cnpjTomador,
            'modoJson': modoJson,
            'xmlCte': xmlCte
        }

        dadosRetorno = validarRastreamento(adapter, adapter_alfa, dadosApi)
        return dadosRetorno

    except Exception as erro:
        # Loga o erro completo com o traceback
        logger.critical(str(erro))
        logger.error(traceback.format_exc())
        
        # Retorno de erro genérico para o cliente, escondendo detalhes internos
        return make_response(jsonify({'error': "Erro crítico na consulta principal"}), 500)

if __name__ == "__main__":
    app.run()
