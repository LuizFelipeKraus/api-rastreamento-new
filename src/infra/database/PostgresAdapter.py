import os
from psycopg2 import extras


class PostgresAdapter:
    def __init__(self, conexao, encoding, logger):
        self.conexao = conexao
        self.logger = logger
        self.conexao.set_client_encoding(encoding)

    def selecionar(self, query, parametros=None):
        try:
            cursor = self.conexao.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SET application_name = %s", [os.environ.get('APPLICATION_NAME', 'Python Application')])
            cursor.execute(query, parametros)
            resultado = cursor.fetchall()
            cursor.close()
            return resultado

        except Exception as erro:
            self.conexao.rollback()
            self.logger.error(f"Erro inesperado no selecionar: {erro} - {query} - {parametros}")

    def selecionar_um(self, query, parametros=None):
        try:
            cursor = self.conexao.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SET application_name = %s", [os.environ.get('APPLICATION_NAME', 'Python Application')])
            cursor.execute(query, parametros)
            resultado = cursor.fetchone()
            cursor.close()
            return resultado

        except Exception as erro:
            self.conexao.rollback()
            self.logger.error(f"Erro inesperado no selecionar_um: {erro} - {query} - {parametros}")

    def existe(self, query, parametros=None):
        try:
            cursor = self.conexao.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SET application_name = %s", [os.environ.get('APPLICATION_NAME', 'Python Application')])
            cursor.execute(query, parametros)
            resultado = cursor.fetchone()
            cursor.close()
            if resultado and len(resultado) > 0:
                return True
            else:
                return False

        except Exception as erro:
            self.conexao.rollback()
            self.logger.error(f"Erro inesperado no existe: {erro} - {query} - {parametros}")

    def executar(self, query, parametros=None):
        try:
            cursor = self.conexao.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute("SET application_name = %s", [os.environ.get('APPLICATION_NAME', 'Python Application')])
            cursor.execute(query, parametros)

            if "RETURNING" in query:
                resultado = cursor.fetchone()
                cursor.close()
                return resultado

            else:
                cursor.close()

        except Exception as erro:
            self.conexao.rollback()
            self.logger.error(f"Erro inesperado no executar: {erro} - {query} - {parametros}")
