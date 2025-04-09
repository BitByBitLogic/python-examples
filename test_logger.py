import pytest
import logging
import os
from pathlib import Path
from src.helpers.logging.logger import Logger

# Static path to logger configuration file
CONFIG_FILE = Path(__file__).parent / "test_logger.config"


@pytest.fixture(scope="module")
def temp_log_dir(tmp_path_factory):
    """Create a temporary directory for logs"""
    return tmp_path_factory.mktemp("tmp")


@pytest.fixture(scope="function")
def logger():
    """Set up the logger using a static config file"""
    Logger.setup_logging(config_path=str(CONFIG_FILE))
    yield Logger.get_logger("test_logger")

    # Clean up logging handlers after each test
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def test_logger_creation(logger):
    """Verify logger instance is created"""
    assert logger is not None
    assert isinstance(logger, logging.Logger)


def test_log_file_creation():
    """Verify log file is created on disk"""
    log_file = Path("logs/test.log")
    assert log_file.exists()


def test_log_levels(logger):
    """Ensure all log levels are written to file"""
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    log_content = Path("logs/test.log").read_text()
    assert "DEBUG - test_log_levels:" in log_content
    assert "INFO - test_log_levels:" in log_content
    assert "WARNING - test_log_levels:" in log_content
    assert "ERROR - test_log_levels:" in log_content
    assert "CRITICAL - test_log_levels:" in log_content


def test_log_format(logger):
    """Check formatting of a log entry"""
    logger.info("Test message")
    log_content = Path("logs/test.log").read_text()
    assert "INFO - test_log_format:" in log_content
    assert "Test message" in log_content


def test_console_output(capsys):
    """Ensure log messages are printed to console"""
    Logger.setup_logging(config_path=str(CONFIG_FILE))
    logger = Logger.get_logger("test_logger")
    logger.info("Console test")
    captured = capsys.readouterr()
    assert "Console test" in captured.out


def test_error_handling():
    """Trigger failure with invalid config path"""
    with pytest.raises(Exception):
        Logger.setup_logging(config_path="/nonexistent/path/to/config")


def test_multiple_loggers():
    """Test independent loggers writing to the same file"""
    Logger.setup_logging(config_path=str(CONFIG_FILE))
    logger1 = Logger.get_logger("logger1")
    logger2 = Logger.get_logger("logger2")

    logger1.info("Message from logger1")
    logger2.info("Message from logger2")

    log_content = Path("logs/test.log").read_text()
    assert "logger1 - INFO - test_multiple_loggers:" in log_content
    assert "Message from logger1" in log_content
    assert "logger2 - INFO - test_multiple_loggers:" in log_content
    assert "Message from logger2" in log_content


def test_warning_log(logger, caplog):
    """Capture a warning-level log using caplog"""
    with caplog.at_level(logging.WARNING):
        logger.warning("This is a warning")
    assert "This is a warning" in caplog.text


def test_log_propagation(caplog):
    """Check if logs propagate to parent handlers"""
    Logger.setup_logging(config_path=str(CONFIG_FILE))
    logger = Logger.get_logger("test_logger")
    logger.propagate = True

    with caplog.at_level(logging.DEBUG):
        logger.debug("Propagation test message")
    assert "Propagation test message" in caplog.text


def test_exception_logging(logger):
    """Ensure exceptions are logged with full trace"""
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("An error occurred")

    log_content = Path("logs/test.log").read_text()
    assert "An error occurred" in log_content
    assert "ValueError: Test exception" in log_content
    assert "Traceback (most recent call last):" in log_content


if __name__ == "__main__":
    # Run all tests in verbose mode
    pytest.main([__file__, "-v", "-s"])
