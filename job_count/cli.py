import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal, Union

from pydantic import BaseModel

from job_count import __project_name__, __version__
from job_count.browser import Browser


class CountJobsCliArgs(BaseModel):
    command: Literal["count-jobs"] = "count-jobs"
    input_file: Path
    output_file: Path
    browser: Browser = Browser.CHROME
    no_headless: bool = False
    cookie_dir: Path | None
    verbose: int = 0
    log_file: str | None = None


class LoginCliArgs(BaseModel):
    command: Literal["login"] = "login"
    email: str | None
    password: str | None
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


CliArgs = Union[CountJobsCliArgs, LoginCliArgs, ClearCookiesCliArgs]


def setup_parser() -> ArgumentParser:

    # Root parser
    root_parser = argparse.ArgumentParser(
        prog=__project_name__,
        description=("A CLI tool for counting job postings on LinkedIn."),
        add_help=True,
    )
    root_parser.add_argument(
        "--version", "-V", action="version", version=f"{__project_name__} {__version__}"
    )

    # Logging parser
    logging_parser = argparse.ArgumentParser(add_help=False)
    logging_parser.add_argument(
        "--verbose",
        "-v",
        help="Increase logging verbosity (-vv to increase further).",
        action="count",
        default=0,
    )
    logging_parser.add_argument(
        "--quiet",
        "-q",
        help="Decrease logging verbosity (-qq to decrease further).",
        action="count",
        default=0,
    )
    logging_parser.add_argument(
        "--log-file",
        "-l",
        help="Write logs to this file. Suppresses logging in stdout.",
        required=False,
        default=None,
        type=str,
    )

    command_parsers = root_parser.add_subparsers(
        title="commands", dest="command", required=True
    )

    # Login parser
    login_parser = command_parsers.add_parser(
        "login",
        add_help=True,
        parents=[logging_parser],
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

    # Count jobs parser
    count_jobs_parser = command_parsers.add_parser(
        "count-jobs",
        add_help=True,
        parents=[logging_parser],
        description="Count the number of job postings on LinkedIn for a list of job titles and locations.",
    )
    count_jobs_parser.add_argument(
        "input_file",
        metavar="input-file",
        help=(
            "The path to the .csv input file containing the job titles and locations to"
            " search for."
        ),
        type=str,
    )
    count_jobs_parser.add_argument(
        "output_file",
        help="The path to the .csv output file to write the job counts to.",
        metavar="output-file",
        type=str,
    )
    count_jobs_parser.add_argument(
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
    count_jobs_parser.add_argument(
        "--no-headless",
        "-N",
        help="Run the tool in a headed browser window.",
        required=False,
        action="store_true",
    )
    count_jobs_parser.add_argument(
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

    # Clear cookies parser
    clear_cookies_parser = command_parsers.add_parser(
        "clear-cookies",
        add_help=True,
        parents=[logging_parser],
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

    return root_parser


def parse_args(parser: ArgumentParser) -> CliArgs:
    args_raw = parser.parse_args()
    match args_raw.command:
        case "login":
            args = LoginCliArgs.model_validate(vars(args_raw))
        case "count-jobs":
            args = CountJobsCliArgs.model_validate(vars(args_raw))
        case "clear-cookies":
            args = ClearCookiesCliArgs.model_validate(vars(args_raw))
        case _:
            raise ValueError(f"Invalid command: {args_raw.command}")
    return args
