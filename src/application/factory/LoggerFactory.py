import logging


class LoggerFactory:
    @staticmethod
    def create_logger(nome, caminho_arquivo=None, terminal=True):
        logger = logging.getLogger(nome)
        logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if caminho_arquivo is not None:
            arquivo = logging.FileHandler(caminho_arquivo)
            arquivo.setFormatter(formatter)
            logger.addHandler(arquivo)

        if terminal:
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)

        return logger

    @staticmethod
    def update_logger(nome):
        logger = logging.getLogger(nome)
        logger.setLevel(logging.ERROR)
        return logger
