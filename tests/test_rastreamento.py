import unittest
import requests


class TestRastreamento(unittest.TestCase):
    def setUp(self):
        self.url_base = "http://localhost:8009/rastreamento/"
        # self.url_base = "https://api.alfatransportes.com.br/rastreamento/"

    def test_1_erro(self):
        json = {
            'idr': '473nb4j67vb96j3zz1zv6n675212852',
            'merNF': 123456789987654321,
            'modoJson': 1
        }

        response = requests.post(self.url_base, json=json)
        response_json = response.json()

        self.assertEqual(response_json['Status'], 9)
        self.assertEqual(response_json['Nome'], 'NOTA FISCAL NAO ENCONTRADA NESTE CNPJ')

    def test_2_consulta(self):
        json = {
            'idr': '473nb4j67vb96j3zz1zv6n675212852',
            'merNF': 6138,
            'modoJson': 1
        }

        response = requests.post(self.url_base, json=json)
        response_json = response.json()

        self.assertEqual(response_json['status'], 2)
        self.assertEqual(response_json['nome'], 'RASTREAMENTO CONCLUIDO COM SUCESSO')
        self.assertEqual(response_json['dadosCte']['numeroCte'], 802289)
        self.assertEqual(response_json['dadosEntrega']['urlComprovante'], 'https://areadocliente.alfatransportes.com.br/comprovante_safe.php?cte=MTI0LzgwMjI4OQ==')

    def test_3_bloqueio_ip(self):
        # Chave incorreta
        response = requests.post(self.url_base, json={"idr": "abc123"})
        self.assertEqual(response.json(), {"error": "chave de acesso incorreta"})

        # Chave incorreta
        response = requests.post(self.url_base, json={"idr": "abc123"})
        self.assertEqual(response.json(), {"error": "chave de acesso incorreta"})

        # Chave incorreta
        response = requests.post(self.url_base, json={"idr": "abc123"})
        self.assertEqual(response.json(), {"error": "chave de acesso incorreta"})

        # Bloqueio por IP
        response = requests.post(self.url_base, json={"idr": "abc123"})
        self.assertIn('Acesso bloqueado para o IP', response.json()['error'])


if __name__ == '__main__':
    unittest.main()
