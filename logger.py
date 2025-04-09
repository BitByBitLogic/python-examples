import logging
import logging.config
from pathlib import Path


class Logger:
    @staticmethod
    def setup_logging(config_path='logger.config'):
        """
        Set up logging configuration using a config file.

        Args:
            config_path (str): Path to the logging configuration file.
        """
        try:
            config_file = Path(config_path)

            # Ensure the config file exists
            if not config_file.is_file():
                raise FileNotFoundError(f"Logging config file not found: {config_file.resolve()}")

            # Load logging configuration from file
            logging.config.fileConfig(config_file, disable_existing_loggers=False)

            # Log confirmation message
            logging.getLogger(__name__).info(f"Logging configured from: {config_file.resolve()}")
        except Exception as e:
            # Print and re-raise any setup exceptions
            print(f"Failed to set up logging: {str(e)}")
            raise

    @staticmethod
    def get_logger(name):
        """
        Retrieve a logger by name.

        Args:
            name (str): The name of the logger.

        Returns:
            logging.Logger: The requested logger instance.
        """
        return logging.getLogger(name)


if __name__ == "__main__":
    # Configure logging using default logger.config
    Logger.setup_logging()

    # Get logger for the current module
    logger = Logger.get_logger(__name__)

    # Emit log messages at different severity levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
