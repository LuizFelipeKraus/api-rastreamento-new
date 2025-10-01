import base64

class TratativasDAO:
    def __init__(self, conexao, conexao_alfa):
        self.conexao = conexao
        self.conexao_alfa = conexao_alfa

    def retornoErros(self, numeroErro):
        tiposErros = {
            1: 'RASTREAMENTO NAO CONCLUIDO',
            2: 'RASTREAMENTO CONCLUIDO COM SUCESSO',
            3: 'FALHA DE CONEXAO COM BANCO DE DADOS',
            4: 'FALTA IDENTIFICACAO DO REMETENTE DA NOTA',
            5: 'FALHA AO VERIFICAR IDENTIFICACAO',
            6: 'IDENTIFICACAO NAO ENCONTRADA',
            7: 'FALHA AO RECUPERAR OS DADOS DA NOTA FISCAL',
            8: 'FALTA NOTA FISCAL DA MERCADORIA',
            9: 'NOTA FISCAL NAO ENCONTRADA NESTE CNPJ',
            10 : 'NOTA INVALIDA'
        }

        return numeroErro, tiposErros.get(numeroErro)

    def converterSerial(self, serial):
        sql = "SELECT emp004_ser, doc020_numero FROM doc020 WHERE doc020_ser = %s LIMIT 1;"
        parametros = [serial]
        dados = self.conexao.selecionar_um(sql, parametros)
        filial = dados['emp004_ser']
        numeroDocumento = dados['doc020_numero']
        return filial, numeroDocumento

    def buscarDadosCte(self, serialCliente, numeroNota):
        sql = """
            SELECT
                doc020.doc020_ser AS ctr_serial,
                doc020.emp004_ser AS ctr_filial,
                doc020.doc020_serie AS ctr_serie,
                doc020.doc020_numero AS ctr_nrodoc,
                doc020.doc020_data_hora::date AS ctr_data,
                doc034_ent.doc034_data_hora::date AS ctr_dtaent,
                opr030.cli004_fim_cli AS ctr_coddes,
                doc022.doc022_numero AS ctr_nf,
                loc003.loc003_cidade||'-'|| loc003.loc003_uf AS ctr_cidade,
                opr030.opr030_fim_cep AS cep_dest,
                doc020.doc020_valor AS valor_cte,
                doc034_prev.doc034_data_hora::date AS previsao_entrega,
                opr030.emp003_fim_und AS ctr_fildes,
                doc020.emp004_ser AS ctr_ag_loc
            FROM doc020
                LEFT JOIN opr030 ON opr030.opr030_codigo = doc020.doc020_ser
                LEFT JOIN doc022 ON doc022.doc020_ser = doc020.doc020_ser
                LEFT JOIN loc003 ON loc003.loc003_ser = opr030.loc003_fim_praca
                LEFT JOIN doc034 doc034_ent ON doc020.doc020_ser = doc034_ent.doc020_ser AND doc034_ent.doc033_ser = 4
                LEFT JOIN doc034 doc034_prev ON doc020.doc020_ser = doc034_prev.doc020_ser AND doc034_prev.doc033_ser = 5
            WHERE doc022.doc022_numero = %s
                AND doc020.cli004_ser = %s
                AND doc020.emp004_ser != 99
                AND doc020.doc004_ser = 1
                AND doc020.doc003_ser IN (3, 8)
            ORDER BY 1 DESC LIMIT 1;
        """
        parametros = [numeroNota, serialCliente]
        dadosCte = self.conexao.selecionar_um(sql, parametros)
        return dadosCte if dadosCte else 9

    def buscarNotas(self, serialCte):
        sql = "SELECT doc022_numero as numero_nota, doc022_serie as serie_nota, doc022_chave as chave_nota FROM doc022 WHERE doc020_ser = %s"
        parametros = [serialCte]
        dados_notas = self.conexao.selecionar(sql, parametros)
        lista_dados_notas= []
        if dados_notas:
            for dados_notas_raw in dados_notas:
        
                notas_formatado = {
                    "numeroNota": str(dados_notas_raw['numero_nota']),
                    "serieNota": str(dados_notas_raw['serie_nota']),
                    "chaveNota": str(dados_notas_raw['chave_nota']),
                }
                lista_dados_notas.append(notas_formatado)
        return lista_dados_notas

    def buscarDadosDestinatario(self, serialCte):
        sql = """
            SELECT
                cli004.cli004_razao AS nome
            FROM doc021
                LEFT JOIN cli004 ON cli004.cli004_ser = doc021.cli004_ser
            WHERE doc021.doc020_ser = %s
                AND doc021.doc002_ser = 2
            LIMIT 1;
        """
        parametros = [serialCte]
        nomeDestinatario = self.conexao.selecionar_um(sql, parametros)
        return nomeDestinatario['nome'] if nomeDestinatario else ''

    def dadosComprovanteEntrega(self, serialCte):
        sql = """
            SELECT
                opr082.opr082_recebedor_nome AS oco_nome_rec,
                opr082.opr082_datahora_ocorrencia AS oco_data_hora,
                opr082.opr082_aplicacao AS oco_origem,
                opr082.emp004_ser AS sco03_filial,
                opr082.doc020_numero AS sco04_nrodoc,
                opr082.opr082_latitude AS oco_latitude,
                opr082.opr082_longitude AS oco_longitude
            FROM opr082
            WHERE opr082.doc020_ser = %s
                AND opr082.opr082_status = 1
            LIMIT 1;
        """
        parametros = [serialCte]
        dadosEntrega = self.conexao.selecionar_um(sql, parametros)
        return dadosEntrega if dadosEntrega else None

    def buscarDadosTomador(self, chaveAPi, cnpjTomador):
        sql = """
            SELECT
                web07_cnpj
            FROM web07
            WHERE web07_chave = %s
            LIMIT 1;
        """
        parametros = [chaveAPi]
        retornoDados = self.conexao.selecionar_um(sql, parametros)
        if not retornoDados:
            return 5

        if cnpjTomador:
            cnpjApi = cnpjTomador
        else:
            cnpjApi = retornoDados['web07_cnpj']

        sql = """
            SELECT
                cli004.cli004_ser AS serial_tomador,
                cli004.cli004_cnpj AS cnpj,
                loc003.loc003_cidade AS cidade,
                cli004.cli004_razao AS nome,
                cli004.cli004_cep AS cep
            FROM cli004
                LEFT JOIN loc003 ON loc003.loc003_ser = cli004.loc003_ser
            WHERE cli004.cli004_cnpj =  %s
            LIMIT 1;
        """
        parametros = [cnpjApi]
        dadosRemetente = self.conexao.selecionar_um(sql, parametros)
        return dadosRemetente if dadosRemetente else 5

    def buscaManifestos(self, serial):
        sql = """
            SELECT
                opr056.opr055_ser AS cod_remanifesto,
                opr025.emp003_origem AS origem,
                opr025.emp003_destino AS destino,
                TO_CHAR(opr055.opr055_saida, 'YYYY-MM-DD -- HH24:MI') AS hora_remanifesto,
                TO_CHAR(opr055.opr055_encerra, 'YYYY-MM-DD -- HH24:MI') AS hora_chegada
            FROM opr056
                LEFT JOIN opr055 ON opr055.opr055_ser = opr056.opr055_ser
                LEFT JOIN opr025 ON opr025.opr025_codigo = opr055.opr025_trecho
                LEFT JOIN opr030 ON opr030.opr030_codigo = opr056.opr030_codigo
            WHERE opr056.opr030_codigo = %s
            ORDER BY hora_remanifesto ASC;
        """
        parametros = [serial]

        lista_remanifestos_raw = self.conexao.selecionar(sql, parametros)
        lista_remanisfestos_formatada = []

        for remanifesto_raw in lista_remanifestos_raw:
            cidadeOrigem = self.buscarCidade(remanifesto_raw['origem'])
            cidadeDestino = self.buscarCidade(remanifesto_raw['destino'])

            remanifesto_formatado = {
                "codigoViagem": remanifesto_raw['cod_remanifesto'],
                "cidadeOrigem": cidadeOrigem.strip(),
                "cidadeDestino": cidadeDestino.strip(),
                "horaSaida": str(remanifesto_raw['hora_remanifesto']),
                "horaChegada": str(remanifesto_raw['hora_chegada'])
            }
            lista_remanisfestos_formatada.append(remanifesto_formatado)
            
        return lista_remanisfestos_formatada

    
    def buscarCidade(self, agencia):
        sql = "SELECT loc003_cidade as cidade FROM emp003 INNER JOIN loc003 ON loc003.loc003_ser = emp003.loc003_ser WHERE emp003_ser = %s LIMIT 1;"
        parametros = [agencia]
        dadosCidade = self.conexao.selecionar_um(sql, parametros)
        return dadosCidade.get('cidade', '')
    
    def buscarAgencia(self, NumeroAgencia):
        sql = """
            SELECT
                loc003.loc003_cidade AS cidade,
                emp002.emp002_fantasia AS nome,
                emp002.emp002_cnpj AS cnpj
            FROM emp003
                LEFT JOIN emp002 ON emp002.emp002_ser = emp003.emp002_ser
                LEFT JOIN loc003 ON loc003.loc003_ser = emp003.loc003_ser
            WHERE emp003_ser = %s
            LIMIT 1;
        """
        parametros = [NumeroAgencia]
        dadosAgencia = self.conexao.selecionar_um(sql, parametros)
        return dadosAgencia

    def saidaEntrega(self, serial):
        sql = """
            SELECT
                TO_CHAR(rom004_data::date, 'YYYY-MM-DD -- HH24:MI') AS hora_saida_entrega
            FROM rom004
            WHERE doc020_ser = %s
            ORDER BY 1 DESC LIMIT 1;
        """
        parametros = [serial]
        dados = self.conexao.selecionar_um(sql, parametros)

        return dados['hora_saida_entrega'] if dados else None

    def buscarCaminhoXml(self, serial):
        sql = """
            SELECT
                '/cte/'
                || TO_CHAR(sco04.sco04_data, 'YYYY')
                || '/'
                || TO_CHAR(sco04.sco04_data, 'MM')
                || '/'
                || cte006.cte002_uf
                || '/'
                ||
                cte006.cte002_chave || '-cte.xml' AS nome
            FROM cte006
                INNER JOIN sco04 ON sco04.sco04_serial = cte006.sco04_serial
            WHERE sco04.sco04_serial = %s
            LIMIT 1;
        """
        parametros = [serial]
        dados = self.conexao_alfa.selecionar_um(sql, parametros)

        return dados['nome'] if dados else None

    def lerXml(self, caminho):
        with open(caminho, 'rb') as file:
            conteudoXml = file.read()
            xmlBase64 = base64.b64encode(conteudoXml).decode('utf-8')

        return xmlBase64


    def buscarOcorrenciasCte(self, serialCte):
        sql = """
            SELECT
                oco002_cod_cliente AS codigoOcorrencia,
                oco003_descricao AS descricaoOcorrencia,
                TO_CHAR(oco003_data, 'DD/MM/YYYY') || ' ' || TO_CHAR(oco003_hora, 'HH24:MI') AS dataOcorrencia
            FROM
                oco003
                JOIN doc020 ON doc020.doc020_ser = oco003.doc020_ser
            WHERE
                oco003.doc020_ser = %s
            ORDER BY oco003_data, oco003_ser ASC;
        """
        parametros = [serialCte]
        ocorrenciasCte = self.conexao.selecionar(sql, parametros)

        return ocorrenciasCte
    
    def buscarComplementar(self, serialCte):
        sql = """
            SELECT 
                doc004_descricao as tipo_cte,
                doc020_valor as valor_complementar,
                doc020_numero as numero_complementar,
                doc020_serie as serie_complementar
            FROM doc027
            LEFT JOIN doc020 ON doc020.doc020_ser = doc027.doc020_complemt
            LEFT JOIN doc004 ON doc004.doc004_ser = doc020.doc004_ser
            WHERE doc020_original = %s AND doc003_ser in (3, 8)
        """
        parametros = [serialCte]
        dados_complementar = self.conexao.selecionar(sql, parametros)
        lista_dados_complementar = []
        if dados_complementar:
            for dados_complementar_raw in dados_complementar:
        
                remanifesto_formatado = {
                    "tipoCteComplementar": str(dados_complementar_raw['tipo_cte']),
                    "numeroCteComplementar": str(dados_complementar_raw['numero_complementar']),
                    "serieCteComplementar": str(dados_complementar_raw['serie_complementar']),
                    "valorCteComplementar": str(dados_complementar_raw['valor_complementar'])

                }
                lista_dados_complementar.append(remanifesto_formatado)
        return lista_dados_complementar