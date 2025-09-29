import os
from datetime import datetime


QTD_TENTATIVAS_LOGIN = int(os.environ.get('QTD_TENTATIVAS_LOGIN'))
MINUTOS_BLOQUEIO = int(os.environ.get('MINUTOS_BLOQUEIO'))


class IpController:
    def __init__(self, logger):
        self.logger = logger
        self.ips_tentativas = {}
        self.ips_bloqueados = {}

    def pegar_ip(self, request):
        if request.headers.getlist("X-Forwarded-For"):
            return request.headers.getlist("X-Forwarded-For")[0]
        else:
            return request.remote_addr

    def bloquear(self, ip):
        self.logger.warning(f"IP {ip} bloqueado!")
        self.ips_bloqueados[ip] = datetime.now()

    def desbloquear(self, ip):
        self.logger.warning(f"IP {ip} desbloqueado!")
        if ip in self.ips_bloqueados:
            self.ips_bloqueados.pop(ip)

    def verificar_bloqueio(self, ip):
        if ip not in self.ips_bloqueados:
            return False

        if ip in self.ips_bloqueados:
            datahora_bloqueio = self.ips_bloqueados[ip]
            datahora_atual = datetime.now()
            diferenca = datahora_atual - datahora_bloqueio
            diferenca_em_minutos = diferenca.total_seconds() / 60
            if diferenca_em_minutos >= MINUTOS_BLOQUEIO:
                self.desbloquear(ip)
                return False

        return True

    def limpar_tentativas(self, ip):
        self.ips_tentativas[ip] = 0

    def nova_tentativa(self, ip):
        self.logger.info(f'Nova tentativa para o IP {ip}')

        if ip in self.ips_tentativas:
            self.ips_tentativas[ip] += 1
        else:
            self.ips_tentativas[ip] = 1

        if self.ips_tentativas[ip] >= QTD_TENTATIVAS_LOGIN:
            self.bloquear(ip)
            self.limpar_tentativas(ip)

        self.logger.info(f"Quantidade de tentativas para o IP {ip}: {self.ips_tentativas[ip]}")
