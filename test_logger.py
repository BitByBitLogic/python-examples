import pytest
import logging
import os
from pathlib import Path
from src.helpers.logging.logger import Logger

LOGGER_CONFIG_TEMPLATE = """
[loggers]
keys=root,{logger_name}

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=defaultFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler,fileHandler

[logger_{logger_name}]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname={logger_name}
propagate=1

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=defaultFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=logging.handlers.RotatingFileHandler
level=DEBUG
formatter=defaultFormatter
args=('{log_path}', 'a', 1048576, 5)

[formatter_defaultFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
"""

@pytest.fixture(scope="module")
def temp_log_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("tmp")

@pytest.fixture(scope="function")
def logger_config_file(temp_log_dir):
    log_path = temp_log_dir / "test.log"
    config_path = temp_log_dir / "logger.config"
    config_text = LOGGER_CONFIG_TEMPLATE.format(
        logger_name="test_logger",
        log_path=log_path.as_posix()
    )
    config_path.write_text(config_text)
    return config_path

@pytest.fixture(scope="function")
def logger(temp_log_dir, logger_config_file):
    Logger.setup_logging(config_path=str(logger_config_file))
    yield Logger.get_logger("test_logger")
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def test_logger_creation(logger):
    assert logger is not None
    assert isinstance(logger, logging.Logger)

def test_log_file_creation(temp_log_dir):
    log_file = temp_log_dir / "test.log"
    assert log_file.exists()

def test_log_levels(logger, temp_log_dir):
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    log_content = (temp_log_dir / "test.log").read_text()
    assert "DEBUG - test_log_levels:" in log_content
    assert "INFO - test_log_levels:" in log_content
    assert "WARNING - test_log_levels:" in log_content
    assert "ERROR - test_log_levels:" in log_content
    assert "CRITICAL - test_log_levels:" in log_content

def test_log_format(logger, temp_log_dir):
    logger.info("Test message")
    log_content = (temp_log_dir / "test.log").read_text()
    assert "INFO - test_log_format:" in log_content
    assert "Test message" in log_content

def test_console_output(temp_log_dir, logger_config_file, capsys):
    Logger.setup_logging(config_path=str(logger_config_file))
    logger = Logger.get_logger("test_logger")
    logger.info("Console test")
    captured = capsys.readouterr()
    assert "Console test" in captured.out

def test_error_handling():
    with pytest.raises(Exception):
        Logger.setup_logging(config_path="/nonexistent/logger.config")

def test_multiple_loggers(temp_log_dir):
    log_file = temp_log_dir / "multi_test.log"
    config_path = temp_log_dir / "multi_logger.config"
    config_text = LOGGER_CONFIG_TEMPLATE.format(
        logger_name="multi_logger",
        log_path=log_file.as_posix()
    )
    config_path.write_text(config_text)
    Logger.setup_logging(config_path=str(config_path))

    logger1 = Logger.get_logger("multi_logger")
    logger2 = Logger.get_logger("multi_logger")

    logger1.info("Message from logger1")
    logger2.info("Message from logger2")

    log_content = log_file.read_text()
    assert "multi_logger - INFO - test_multiple_loggers:" in log_content
    assert "Message from logger1" in log_content
    assert "Message from logger2" in log_content

def test_warning_log(logger, caplog):
    with caplog.at_level(logging.WARNING):
        logger.warning("This is a warning")
    assert "This is a warning" in caplog.text

def test_log_propagation(temp_log_dir):
    log_file = temp_log_dir / "propagation_test.log"
    config_path = temp_log_dir / "propagation.config"
    config_text = LOGGER_CONFIG_TEMPLATE.format(
        logger_name="propagation_test",
        log_path=log_file.as_posix()
    )
    config_path.write_text(config_text)
    Logger.setup_logging(config_path=str(config_path))

    logger = Logger.get_logger("propagation_test")
    logger.propagate = True

    logger.debug("Propagation test message")
    log_content = log_file.read_text()
    assert "Propagation test message" in log_content

def test_exception_logging(logger, temp_log_dir):
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("An error occurred")

    log_content = (temp_log_dir / "test.log").read_text()
    assert "An error occurred" in log_content
    assert "ValueError: Test exception" in log_content
    assert "Traceback (most recent call last):" in log_content

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
