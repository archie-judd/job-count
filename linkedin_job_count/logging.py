import logging
import sys
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


def log_uncaught_exceptions(exctype, value, tb):
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))


def setup_logging(level: int, filename: str | None = None):

    handlers = []
    if filename:
        # Max log file size of 1MB, backing up 5 before deletion
        file_handler = RotatingFileHandler(
            filename, mode="a", maxBytes=1024 * 1024, backupCount=5
        )
        handlers.append(file_handler)

    else:
        stream_handler = StreamHandler()
        handlers.append(stream_handler)

    logging.basicConfig(
        handlers=handlers,
        level=level,
        format="%(asctime)s: %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S %Z",
    )

    # Install exception handler
    sys.excepthook = log_uncaught_exceptions


def get_log_level_for_verbosity(verbosity: int) -> int:

    if verbosity <= -2:
        log_level = logging.CRITICAL
    elif verbosity == -1:
        log_level = logging.ERROR
    elif verbosity == 0:
        log_level = logging.WARNING
    elif verbosity == 1:
        log_level = logging.INFO
    elif verbosity >= 2:
        log_level = logging.DEBUG
    else:
        assert False, "unreachable"

    return log_level
