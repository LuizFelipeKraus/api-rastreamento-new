import base64
from flask import make_response
from markupsafe import escape


def converterBase64(cte):
    validar_string = cte.encode('utf-8')
    base64_string = base64.b64encode(validar_string).decode('utf-8')
    return base64_string


def urlComprovanteEntrega(serialCte, filialCte, numeroCte):
    url = "https://arearestrita.alfatransportes.com.br/acompanhamento/comprovante_entrega/"
    cte = str(serialCte)
    cte64 = converterBase64(cte)
    url_completa = url + cte64 + f"/{filialCte}_{numeroCte}"
    return url_completa


def modeloRetorno(numeroEstado, nomeRetorno, modeloJson, dadosEmbarque={}, dadosEntrega={}, dadosNota={}, dadosTransportadora={}, dadosRemetente={}, saidaParaEntrega='', dadosOcorrencias={}, xmlBase64='', serialCte = '', dadosComplementar = {}):
    modelo = gerarJson(numeroEstado, nomeRetorno, dadosEmbarque, dadosEntrega, dadosNota, dadosTransportadora, dadosRemetente, saidaParaEntrega, dadosOcorrencias, xmlBase64, serialCte, dadosComplementar)
    return modelo


def gerarJson(numeroEstado, nomeRetorno, dadosEmbarque={}, dadosEntrega={}, dadosNota={}, dadosTransportadora={}, dadosRemetente={}, saidaParaEntrega='', dadosOcorrencias={}, xmlBase64='', serialCte = '', dadosComplementar = {}):
    json = {
        "Status": numeroEstado,
        "Nome": nomeRetorno
    }

    if numeroEstado == 2:
        if dadosEntrega:
            Entrega = {
                "recebedorMercadoria": dadosEntrega['oco_nome_rec'].title(),
                "dataEntrega": str(dadosEntrega['oco_data_hora']),
                "urlComprovante": urlComprovanteEntrega(serialCte, str(dadosEntrega['sco03_filial']), str(dadosEntrega['sco04_nrodoc'])),
                "latitude": str(dadosEntrega['oco_latitude']),
                "longitude": str(dadosEntrega['oco_longitude'])
            }
        else:
            Entrega = ""
        json = {
            "status": numeroEstado,
            "nome": nomeRetorno,
            "dadosTransportadora": {
                "nomeTransportadora": str(dadosTransportadora['nome']).strip(),
                "cnpjTransportadora": dadosTransportadora['cnpj'],
                "cidadeTransportadora": str(dadosTransportadora['cidade']).strip()
            },
            "dadosRemetente": {
                "nomeRemetente": dadosRemetente['nome'],
                "cnpjRemetente": dadosRemetente['cnpj']
            },
            "dadosCte": {
                "notas": dadosNota['notas'],
                "numeroCte": dadosNota['numeroCte'],
                "valorCte": dadosNota['valorCte'],
                "dataEmissao": str(dadosNota['dataInicio']),
                "dataPrivista": str(dadosNota['dataPrevista']),
                "nomeDestinatario": dadosNota['nomeTomador'],
                "agenciaInicio": str(dadosNota['agenciaInicio']).strip(),
                "agenciaFim": str(dadosNota['agenciaDestino']).strip(),
                "cidadeEntrega": str(dadosNota['cidadeCalculo']).strip(),
                "xmlCte": xmlBase64 if xmlBase64 else ''
            },
            
            "dadosEmbarque": dadosEmbarque,
            "dadosEntrega": Entrega,
            "dadosComplementar": dadosComplementar
        }
        json['ocorrenciasExtras'] = []
        for dado in dadosOcorrencias:
            ocorrencia = {
                "codigoOcorrencia": dado['codigoocorrencia'],
                "descricaoOcorrencia": dado['descricaoocorrencia'],
                "dataOcorrencia": dado['dataocorrencia']
            }
            json["ocorrenciasExtras"].append(ocorrencia)

    return json
