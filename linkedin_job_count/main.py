import csv
import datetime as dt
import logging
import os
import re
from pathlib import Path

from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin_job_count import __project_name__, __version__
from linkedin_job_count.cli import setup_parser
from linkedin_job_count.logging import get_log_level_for_verbosity, setup_logging

logger = logging.getLogger(__name__)


class Environment(BaseModel):
    LINKEDIN_EMAIL: str | None = None
    LINKEDIN_PASSWORD: str | None = None


class Job(BaseModel):
    job_title: str
    location: str


class JobWithCount(Job):
    ts: dt.datetime
    count: int


LINKEDIN_BASE_URL = "https://www.linkedin.com"


def read_jobs_to_search_for(file_path: Path) -> list[Job]:
    with open(file_path, mode="r", encoding="utf-8") as file:
        return [Job.model_validate(row) for row in csv.DictReader(file)]


def write_jobs_with_counts(file_path: Path, jobs_with_counts: list[JobWithCount]):
    file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0

    data = [job.model_dump() for job in jobs_with_counts]
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())

        # Write header only if the file does not exist or is empty
        if not file_exists:
            writer.writeheader()

        writer.writerows(data)


def make_job_search_url(job_title: str, location: str) -> str:
    return f"{LINKEDIN_BASE_URL}/jobs/search/?keywords={job_title}&location={location}"


def login_to_linkedin(driver: WebDriver, email: str, password: str):

    driver.get(f"{LINKEDIN_BASE_URL}/login")  # Open the LinkedIn login page

    # Wait for login fields to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))

    # Enter email
    email_input = driver.find_element(By.ID, "username")
    email_input.send_keys(email)

    # Enter password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)  # Press Enter to log in

    # Wait for successful login
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "global-nav"))
    )


def get_job_count(driver: WebDriver, job_title: str, location: str) -> int:

    url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"
    driver.get(url)

    # Wait for job results to load
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


def main():

    parser = setup_parser()
    args = parser.parse_args()

    log_level = get_log_level_for_verbosity(args.verbose)
    setup_logging(log_level, args.log_file)

    environment = Environment.model_validate(os.environ)

    email = args.email or environment.LINKEDIN_EMAIL
    password = args.password or environment.LINKEDIN_PASSWORD

    if email is None:
        logging.error(
            "No email provided - provide an email address using the --email flag, or set the environment variable LINKEDIN_EMAIL"
        )
        raise ValueError("No email provided")

    if password is None:
        logging.error(
            "No password provided - provide a password using the --password flag, or set the environment variable LINKEDIN_PASSWORD"
        )
        raise ValueError("No email provided")

    print(args)
    jobs = read_jobs_to_search_for(args.input_file)

    options = Options()
    if not args.headed:
        options.add_argument("--headless")
    if args.chrome_user_data_dir:
        options.add_argument(f"--user-data-dir={args.chrome_user_data_dir}")

    driver = webdriver.Chrome(options=options)

    driver.get(f"{LINKEDIN_BASE_URL}/feed/")

    if "login" in driver.current_url:
        logger.info("Logging in")
        login_to_linkedin(driver, email, password)
        logger.info("Successfully logged in!")
    else:
        logging.info("Already logged in to LinkedIn")

    jobs_with_counts: list[JobWithCount] = []
    for job in jobs:
        count = get_job_count(driver, job.job_title, job.location)
        logging.info(f"Number of {job.job_title} jobs in {job.location}: {count}")
        job_with_count = JobWithCount(
            job_title=job.job_title,
            location=job.location,
            count=count,
            ts=dt.datetime.now(dt.timezone.utc),
        )
        jobs_with_counts.append(job_with_count)

    write_jobs_with_counts(args.output_file, jobs_with_counts)

    driver.quit()

    logging.info("Done!")
