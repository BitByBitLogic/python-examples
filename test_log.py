import pytest
import logging
import os
from pathlib import Path
from src.helpers.logging.log import Logger

@pytest.fixture(scope="module")
def temp_log_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("tmp")

@pytest.fixture(scope="function")
def logger(temp_log_dir):
    log_file = temp_log_dir / "test.log"
    Logger.setup_logging(log_dir=str(temp_log_dir), log_filename="test.log", log_level=logging.DEBUG)
    yield Logger.get_logger(__name__)
    # Clean up
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

def test_console_output(temp_log_dir, capsys):
    Logger.setup_logging(log_dir=str(temp_log_dir), log_filename="test.log", log_level=logging.DEBUG, console_output=True)
    logger = Logger.get_logger("test_log")
    logger.info("Console test")
    captured = capsys.readouterr()
    assert "Console test" in captured.out

def test_error_handling(temp_log_dir):
    with pytest.raises(Exception):
        Logger.setup_logging(log_dir="/nonexistent/directory")

def test_multiple_loggers(temp_log_dir):
    Logger.setup_logging(log_dir=str(temp_log_dir), log_filename="multi_test.log", log_level=logging.DEBUG)
    logger1 = Logger.get_logger("logger1")
    logger2 = Logger.get_logger("logger2")

    logger1.info("Message from logger1")
    logger2.info("Message from logger2")

    log_content = (temp_log_dir / "multi_test.log").read_text()
    assert "logger1 - INFO - test_multiple_loggers:" in log_content
    assert "Message from logger1" in log_content
    assert "logger2 - INFO - test_multiple_loggers:" in log_content
    assert "Message from logger2" in log_content

def test_warning_log(logger, caplog):
    with caplog.at_level(logging.WARNING):
        logger.warning("This is a warning")
    assert "This is a warning" in caplog.text

def test_log_propagation(temp_log_dir, caplog):
    Logger.setup_logging(log_dir=str(temp_log_dir), log_filename="propagation_test.log", log_level=logging.DEBUG)
    logger = Logger.get_logger("propagation_test")
    logger.propagate = True

    with caplog.at_level(logging.DEBUG):
        logger.debug("Propagation test message")
    assert "Propagation test message" in caplog.text

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
