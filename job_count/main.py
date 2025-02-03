import csv
import datetime as dt
import logging
import re
import sys
from pathlib import Path

import tabulate
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from job_count import __project_name__, __version__
from job_count.browser import (
    DEFAULT_COOKIE_DIR,
    WebDriver,
    clear_cookies,
    get_cookie_path,
    load_cookies,
    make_driver,
    save_cookies,
)
from job_count.cli import (
    ClearCookiesCliArgs,
    LoginCliArgs,
    QueryArgs,
    parse_args,
    setup_parser,
)
from job_count.logging import get_log_level_for_verbosity, setup_logging
from job_count.types import Job, JobWithCount

logger = logging.getLogger(__name__)

LINKEDIN_BASE_URL = "https://www.linkedin.com"


def read_jobs_to_search_for(file_path: Path) -> list[Job]:

    logger.info(f"Readings job to search for from {file_path}")
    with open(file_path, mode="r", encoding="utf-8") as file:
        return [Job.model_validate(row) for row in csv.DictReader(file)]


def write_jobs_with_counts(file_path: Path, jobs_with_counts: list[JobWithCount]):

    file_exists = Path.exists(file_path) and Path(file_path).stat().st_size > 0
    if not file_exists:
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Writing job counts to {file_path}")

    data = [job.model_dump() for job in jobs_with_counts]
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())

        # Write header only if the file does not exist or is empty
        if not file_exists:
            writer.writeheader()

        writer.writerows(data)


def make_job_search_url(job_title: str, location: str) -> str:
    return f"{LINKEDIN_BASE_URL}/jobs/search/?keywords={job_title}&location={location}"


def login_to_linkedin(driver: WebDriver, timeout_s: int, cookie_path: Path):

    driver.get(f"{LINKEDIN_BASE_URL}/login")  # Open the LinkedIn login page

    logger.info("Waiting for successful login...")
    WebDriverWait(driver, timeout_s).until(
        EC.presence_of_element_located((By.ID, "global-nav"))
    )
    logger.info("success!")

    save_cookies(driver, cookie_path)


def get_job_count(driver: WebDriver, job_title: str, location: str) -> int:

    url = f"{LINKEDIN_BASE_URL}/jobs/search/?keywords={job_title}&location={location}"
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    element_list = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'jobs-search-results-list__subtitle')]"
    )
    if element_list:
        div_element = element_list[0]
    else:
        try:
            div_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class, 'jobs-search-results-list__subtitle')]",
                    )
                )
            )
        except:
            div_element = None

    if div_element is not None:
        count = int(re.sub(r"[^\d]", "", div_element.text))
    else:
        raise ValueError("Could not find job count element")

    return count


def handle_login(args: LoginCliArgs):

    cookie_path = get_cookie_path(args.cookie_dir or DEFAULT_COOKIE_DIR, args.browser)
    driver = make_driver(args.browser, False)

    try:
        login_to_linkedin(driver, args.login_timeout, cookie_path)
        driver.quit()
        print(f"Successfully logged in! Cookies saved here: {cookie_path}")
    except TimeoutException:
        driver.quit()
        logger.error(
            "Timeout during login. Please try again. Consider extending the timeout "
            f"with the argument --login-timeout."
        )
        sys.exit(1)


def handle_clear_cookies(
    args: ClearCookiesCliArgs,
):

    cookie_path = get_cookie_path(args.cookie_dir or DEFAULT_COOKIE_DIR, args.browser)
    clear_cookies(cookie_path)

    print("Cookies cleared")


def print_results_table(jobs_with_counts: list[JobWithCount]):
    results_raw: list[dict] = []
    for job in jobs_with_counts:
        result_raw = {k: v for k, v in job.model_dump().items() if k != "ts"}
        results_raw.append(result_raw)
    table = tabulate.tabulate(results_raw, headers="keys", tablefmt="pretty")
    print(table)


def query(
    jobs: list[Job],
    cookie_path: Path,
    driver: WebDriver,
) -> list[JobWithCount]:

    driver.get(f"{LINKEDIN_BASE_URL}/feed/")
    cookies_loaded = load_cookies(driver, cookie_path)

    if not cookies_loaded:
        logger.error("No cookies loaded. run 'job-count login' first.")
        sys.exit(0)
    if "login" in driver.current_url:
        logger.error(
            "Cookies loaded but not logged in. Run 'job-count login' to "
            "relogin first."
        )
        sys.exit(0)

    logger.info("Logged in to LinkedIn")

    jobs_with_counts: list[JobWithCount] = []

    for i, job in enumerate(jobs):

        logger.info(
            f"({i+1}/{len(jobs)}) - Searching for {job.job_title} jobs in {job.location}"
        )

        count = get_job_count(driver, job.job_title, job.location)

        job_with_count = JobWithCount(
            job_title=job.job_title,
            location=job.location,
            count=count,
            ts=dt.datetime.now(dt.timezone.utc),
        )
        jobs_with_counts.append(job_with_count)

    return jobs_with_counts


def handle_query(args: QueryArgs):

    cookie_dir = args.cookie_dir or DEFAULT_COOKIE_DIR
    cookie_path = get_cookie_path(cookie_dir=cookie_dir, browser=args.browser)
    driver = make_driver(browser=args.browser, headless=not args.no_headless)

    if args.input_file:
        jobs = read_jobs_to_search_for(args.input_file)
    elif args.terms:
        jobs = args.terms
    else:
        raise ValueError("Expected either terms or input_file")

    jobs_with_counts = query(jobs=jobs, cookie_path=cookie_path, driver=driver)

    driver.quit()

    print_results_table(jobs_with_counts)

    if args.output_file:
        write_jobs_with_counts(args.output_file, jobs_with_counts)
        print(f"Results written to {args.output_file}")


def main():

    try:
        parser = setup_parser()
        args = parse_args(parser)

        log_level = get_log_level_for_verbosity(args.verbose)
        setup_logging(log_level, args.log_file)

        match args.command:
            case "login":
                handle_login(args)
            case "clear-cookies":
                handle_clear_cookies(args)
            case "query":
                handle_query(args)
            case _:
                raise ValueError(f"Unrecognized command: {args.command}")

        logger.info("Done!")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Exiting early due to keyboard interrupt")
        sys.exit(1)
