from src.gerarRetorno import modeloRetorno
from src.tratativasDados import TratativasDAO


def validarRastreamento(conexao, conexao_alfa, dados):
    tratativas_dao = TratativasDAO(conexao, conexao_alfa)

    tomadorCnpj = dados['cnpjTomador']
    chaveApi = dados['chaveAcessoApi']
    chaveNotaFiscal = dados['chaveNotaFiscal']
    modoJson = dados['modoJson']
    xmlCte = dados['xmlCte']
    dadosTomador = tratativas_dao.buscarDadosTomador(chaveApi, tomadorCnpj)
    if modoJson is not None and modoJson in (1, '1'):
        modoJson = 1
    else:
        modoJson = 0

    if not chaveNotaFiscal:
        numeroStatus, statusRetorno = tratativas_dao.retornoErros(10)
        modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)

    # CHAVE DA NOTA INVALIDA
    if not chaveNotaFiscal.isdigit():
        numeroStatus, statusRetorno = tratativas_dao.retornoErros(10)
        modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)

    # FALTA IDENTIFICACAO
    elif not chaveApi:
        numeroStatus, statusRetorno = tratativas_dao.retornoErros(4)
        modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)

    # FALTA NOTA FISCAL DA MERCADORIA
    elif not chaveNotaFiscal:
        numeroStatus, statusRetorno = tratativas_dao.retornoErros(8)
        modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)

    # FALHA AO VERIFICAR IDENTIFICACAO
    elif dadosTomador == 5:
        numeroStatus, statusRetorno = tratativas_dao.retornoErros(5)
        modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)
    else:
        serialCliente = dadosTomador['serial_tomador']
        dadosCargaTransportes = tratativas_dao.buscarDadosCte(serialCliente, chaveNotaFiscal)

        # NOTA FISCAL NAO ENCONTRADA NESTE CNPJ
        if dadosCargaTransportes == 9:
            numeroStatus, statusRetorno = tratativas_dao.retornoErros(9)
            modelo = modeloRetorno(numeroStatus, statusRetorno, modoJson)
        else:
            dataEntrega = dadosCargaTransportes['ctr_dtaent']
            serialCte = dadosCargaTransportes['ctr_serial']
            #numeroNota = dadosCargaTransportes['ctr_nf']
            numeroNota = tratativas_dao.buscarNotas(serialCte)
            numeroDocumento = dadosCargaTransportes['ctr_nrodoc']
            dataInicio = dadosCargaTransportes['ctr_data']
            cidadeCalculo = dadosCargaTransportes['ctr_cidade']
            numeroFilialOrigem = dadosCargaTransportes['ctr_filial']
            numeroFilialDestino = dadosCargaTransportes['ctr_fildes']
            dataPrevista = dadosCargaTransportes['previsao_entrega']
            valorCte = float(round(dadosCargaTransportes['valor_cte'], 2))

            dadosEmbarque = tratativas_dao.buscaManifestos(serialCte)
            nomeDestinatario = tratativas_dao.buscarDadosDestinatario(serialCte)
            buscarCidadeOrigem = tratativas_dao.buscarCidade(numeroFilialOrigem)
            buscarCidadeDestino = tratativas_dao.buscarCidade(numeroFilialDestino)

            dadosAgencia = tratativas_dao.buscarAgencia(numeroFilialOrigem)
            dadosOcorrencias = tratativas_dao.buscarOcorrenciasCte(serialCte)

            dadosNota = {
                'notas': numeroNota,
                'numeroCte': numeroDocumento,
                'dataInicio': dataInicio,
                'dataPrevista': dataPrevista,
                'valorCte': valorCte,
                'agenciaInicio': buscarCidadeOrigem,
                'agenciaDestino': buscarCidadeDestino,
                'cidadeCalculo': cidadeCalculo,
                'nomeTomador': nomeDestinatario
            }
            saidaParaEntrega = tratativas_dao.saidaEntrega(serialCte)
            # VERIFICA SE TEM DATA DE ENTREGA
            dadosEntrega = []
            if dataEntrega:
                dadosEntrega = tratativas_dao.dadosComprovanteEntrega(serialCte)

            dados_complementar = tratativas_dao.buscarComplementar(serialCte)
            # VERIFICA SE TERA XML DO CTE
            xmlBase64 = ''
            if xmlCte:
                if xmlCte == '1':
                    caminhoXml = tratativas_dao.buscarCaminhoXml(serialCte)
                    xmlBase64 = tratativas_dao.lerXml(caminhoXml)

            numeroStatus, statusRetorno = tratativas_dao.retornoErros(2)
            modelo = modeloRetorno(
                numeroStatus,
                statusRetorno,
                modoJson,
                dadosEmbarque,
                dadosEntrega,
                dadosNota,
                dadosAgencia,
                dadosTomador,
                saidaParaEntrega,
                dadosOcorrencias,
                xmlBase64,
                serialCte,
                dados_complementar
            )

    return modelo
