import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, Self, Union

from pydantic import BaseModel, field_validator, model_validator

from job_count import __project_name__, __version__
from job_count.browser import Browser
from job_count.types import Job


class QueryArgs(BaseModel):
    command: Literal["query"] = "query"
    terms: list[Job] | None = None
    input_file: Path | None = None
    output_file: Path | None = None
    browser: Browser = Browser.CHROME
    no_headless: bool = False
    cookie_dir: Path | None
    verbose: int = 0
    log_file: str | None = None

    @field_validator("terms", mode="before")
    @classmethod
    def parse_jobs(cls, value):
        if value is not None:
            for i, job_raw in enumerate(value):
                if isinstance(job_raw, str):
                    value[i] = Job.from_string(job_raw)
        return value

    @model_validator(mode="after")
    def terms_or_input_file(self) -> Self:
        if (self.terms and self.input_file) or (not self.terms and not self.input_file):
            raise ValueError("Expected terms or input_file but not both.")
        return self


class LoginCliArgs(BaseModel):
    command: Literal["login"] = "login"
    browser: Browser = Browser.CHROME
    cookie_dir: Path | None
    login_timeout: int = 60
    verbose: int = 0
    log_file: str | None = None


class ClearCookiesCliArgs(BaseModel):
    command: Literal["clear-cookies"] = "clear-cookies"
    cookie_dir: Path | None
    verbose: int = 0
    log_file: str | None = None
    browser: Browser = Browser.CHROME


CliArgs = Union[QueryArgs, LoginCliArgs, ClearCookiesCliArgs]


def add_logging_args(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        "--verbose",
        "-v",
        help="Increase logging verbosity (-vv to increase further).",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--quiet",
        "-q",
        help="Decrease logging verbosity (-qq to decrease further).",
        action="count",
        default=0,
    )
    parser.add_argument(
        "--log-file",
        "-l",
        help="Write logs to this file. Suppresses logging in stdout.",
        required=False,
        default=None,
        type=str,
    )
    return parser


def setup_parser() -> ArgumentParser:

    # Root parser
    root_parser = argparse.ArgumentParser(
        prog=__project_name__,
        description=("A CLI tool for counting job postings on LinkedIn."),
        add_help=True,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    root_parser.add_argument(
        "--version", "-V", action="version", version=f"{__project_name__} {__version__}"
    )

    # Logging parser
    command_parsers = root_parser.add_subparsers(
        title="commands", dest="command", required=True
    )

    # Login parser
    login_parser = command_parsers.add_parser(
        "login",
        add_help=True,
        description="Login to LinkedIn to save cookies for future use.",
    )
    login_parser.add_argument(
        "--browser",
        "-b",
        help=(
            "Choose the browser to use. Options are 'chrome' 'firefox'.  Default is "
            "'chrome'."
        ),
        required=False,
        choices=[browser.value for browser in Browser],
        default=Browser.CHROME.value,
        type=str,
    )
    login_parser.add_argument(
        "--cookie-dir",
        "-d",
        help=(
            "Path to a directory for storing cookies (to prevent needing to login each "
            "time). Defaults to ~/.local/share/job-count."
        ),
        required=False,
        default=None,
        type=str,
    )
    login_parser.add_argument(
        "--login-timeout",
        "-t",
        help=("Number of seconds to wait for the login page to load."),
        default=60,
        type=int,
    )
    add_logging_args(login_parser)

    # Query parser
    query_parser = command_parsers.add_parser(
        "query",
        add_help=True,
        description="Count the number of job postings on LinkedIn for a list of job "
        "titles and locations. Query with a string of job titles and locations, or pass"
        " a .csv file with job titles and locations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    query_input = query_parser.add_mutually_exclusive_group(required=True)
    query_input.add_argument(
        "--input-file",
        "-i",
        metavar="input_file",
        help=(
            "The path to the .csv input file containing the job titles and locations to search for. Example format:\njob_title,location\nIce Sculptor,London\nPanda Fluffer,Tokyo\n"
        ),
        type=str,
    )
    query_input.add_argument(
        "--terms",
        "-t",
        nargs="+",
        help=(
            "Space separated list of job titles and locations to search for.  Each job "
            "title and location should be separated by a comma.  For example:\n"
            'job-count query --string "Ice Sculptor,Honolulu" "Panda Fluffer,Tokyo"'
        ),
    )
    query_parser.add_argument(
        "--output-file",
        "-o",
        help="The path to the .csv output file to write the job counts to.",
        metavar="output_file",
        type=str,
        required=False,
    )
    query_parser.add_argument(
        "--browser",
        "-b",
        help=(
            "Choose the browser to use. Options are 'chrome' 'firefox'.  Default is "
            "'chrome'."
        ),
        required=False,
        choices=[browser.value for browser in Browser],
        default=Browser.CHROME.value,
        type=str,
    )
    query_parser.add_argument(
        "--no-headless",
        "-N",
        help="Run the tool in a headed browser window.",
        required=False,
        action="store_true",
    )
    query_parser.add_argument(
        "--cookie-dir",
        "-d",
        help=(
            "Path to a directory for storing cookies (to prevent needing to login each "
            "time). Defaults to ~/.local/share/job-count."
        ),
        required=False,
        default=None,
        type=str,
    )
    add_logging_args(query_parser)

    # Clear cookies parser
    clear_cookies_parser = command_parsers.add_parser(
        "clear-cookies",
        add_help=True,
        description="Clear cookies stored for LinkedIn login.",
    )
    clear_cookies_parser.add_argument(
        "--browser",
        "-b",
        help=(
            "Choose the browser to use. Options are 'chrome' 'firefox'.  Default is "
            "'chrome'."
        ),
        required=False,
        choices=[browser.value for browser in Browser],
        default=Browser.CHROME.value,
        type=str,
    )
    clear_cookies_parser.add_argument(
        "--cookie-dir",
        "-d",
        help=(
            "Path to a directory for storing cookies (to prevent needing to login each "
            "time). Defaults to ~/.local/share/job-count."
        ),
        required=False,
        default=None,
        type=str,
    )
    add_logging_args(clear_cookies_parser)

    return root_parser


def parse_args(parser: ArgumentParser) -> CliArgs:
    args_raw = parser.parse_args()
    match args_raw.command:
        case "login":
            args = LoginCliArgs.model_validate(vars(args_raw))
        case "query":
            args = QueryArgs.model_validate(vars(args_raw))
        case "clear-cookies":
            args = ClearCookiesCliArgs.model_validate(vars(args_raw))
        case _:
            raise ValueError(f"Invalid command: {args_raw.command}")
    return args
