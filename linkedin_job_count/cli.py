import argparse
from argparse import ArgumentParser

from linkedin_job_count import __project_name__, __version__


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
        "--chrome-user-data-dir",
        "-d",
        help=(
            "Path to your chrome user data directory, for storing cookies (to prevent"
            " needing to login each time). This can be found by running "
            "`chrome://version/` in your browser and looking for the 'Profile Path' "
            "field, or you can define a new directory."
        ),
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "--email",
        "-e",
        help=(
            "Your LinkedIn email address. If not provided, the tool will look for the "
            "environment variable LINKEDIN_EMAIL"
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
            "environment variable LINKEDIN_PASSWORD"
        ),
        required=False,
        default=None,
        type=str,
    )
    parser.add_argument(
        "--headed",
        "-H",
        help=(
            "Run the tool in a headed browser window. By default, the tool runs in a "
            "headless window"
        ),
        required=False,
        action="store_true",
    )
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
