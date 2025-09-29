class ValidadorChave:
    def __init__(self, adapter):
        self.adapter = adapter

    def validar(self, chave):
        query = "SELECT web07_codigo FROM web07 WHERE web07_chave = %s LIMIT 1;"
        parametros = [chave]
        chave_valida = self.adapter.existe(query, parametros)
        return chave_valida
