import argparse
from argparse import ArgumentParser
from pathlib import Path

from pydantic import BaseModel

from linkedin_job_count import __project_name__, __version__
from linkedin_job_count.browser import Browser


class CliArgs(BaseModel):
    input_file: Path
    output_file: Path
    email: str | None
    password: str | None
    browser: Browser = Browser.CHROME
    headless: bool = False
    cookie_dir: Path | None
    clear_cookies: bool = False
    login_timeout: int = 30
    verbose: int = 0
    log_file: str | None = None


def setup_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=__project_name__,
        description=("A CLI tool for counting job postings on LinkedIn."),
        add_help=True,
    )
    parser.add_argument(
        "--version", "-V", action="version", version=f"{__project_name__} {__version__}"
    )

    parser.add_argument(
        "input_file",
        metavar="input-file",
        help=(
            "The path to the .csv input file containing the job titles and locations to"
            " search for."
        ),
        type=str,
    )
    parser.add_argument(
        "output_file",
        help="The path to the .csv output file to write the job counts to.",
        metavar="output-file",
        type=str,
    )
    parser.add_argument(
        "--email",
        "-e",
        help=(
            "Your LinkedIn email address. If not provided, the tool will look for the "
            "environment variable LINKEDIN_EMAIL."
        ),
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "--password",
        "-p",
        help=(
            "Your LinkedIn email address. If not provided, the tool will look for the "
            "environment variable LINKEDIN_PASSWORD."
        ),
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
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
    parser.add_argument(
        "--headless",
        "-H",
        help="Run the tool in a headless browser window.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--cookie-dir",
        "-d",
        help=(
            "Path to a directory for storing cookies (to prevent needing to login each "
            "time). Defaults to ~/.local/share/linkedin-job-count."
        ),
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "--clear-cookies",
        "-c",
        help="Clear the cookies before running the tool.",
        required=False,
        action="store_true",
    )
    parser.add_argument(
        "--login-timeout",
        "-t",
        help=("Number of seconds to wait for the login page to load."),
        default=30,
        type=int,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Increase logging verbosity (default is -v, -vv to increase further).",
        action="count",
        default=1,
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


def parse_args(parser: ArgumentParser) -> CliArgs:
    args = CliArgs.model_validate(vars(parser.parse_args()))
    return args
