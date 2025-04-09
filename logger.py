import logging
import logging.config
from pathlib import Path

class Logger:
    @staticmethod
    def setup_logging(config_path='logger.config'):
        try:
            config_file = Path(config_path)
            if not config_file.is_file():
                raise FileNotFoundError(f"Logging config file not found: {config_file.resolve()}")
            logging.config.fileConfig(config_file, disable_existing_loggers=False)
            logging.getLogger(__name__).info(f"Logging configured from: {config_file.resolve()}")
        except Exception as e:
            print(f"Failed to set up logging: {str(e)}")
            raise

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

if __name__ == "__main__":
    Logger.setup_logging()
    logger = Logger.get_logger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
