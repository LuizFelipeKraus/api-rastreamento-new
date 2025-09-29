import requests
import time

def check_status():
    """
    Faz uma requisição GET e verifica o status da resposta JSON.
    """
    url = "https://api.alfatransportes.com.br//rastreamento/status"
    expected_response = {"status": "OK"}

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lança um erro para códigos de status HTTP 4xx/5xx

        # Converte a resposta para JSON
        data = response.json()
        print(f"Resposta recebida: {data}")

        # Verifica se a resposta JSON é a esperada
        if data == expected_response:
            print("Status OK! A API está funcionando como esperado.")
            return True
        else:
            print(f"Status diferente do esperado. Resposta: {data}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return False

def main():
    """
    Loop principal que executa a verificação a cada 10 segundos.
    """
    while True:
        print("\nVerificando o status da API...")
        check_status()
        time.sleep(10)  # Espera 10 segundos antes da próxima verificação

if __name__ == "__main__":
    main()