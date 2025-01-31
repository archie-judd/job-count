import logging
import pickle
from enum import StrEnum
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver

logger = logging.getLogger(__name__)

WebDriver = ChromeWebDriver | FirefoxWebDriver

DEFAULT_COOKIE_DIR = Path("~/.local/share/linkedin-job-count").expanduser()


class Browser(StrEnum):
    CHROME = "chrome"
    FIREFOX = "firefox"


def make_driver(
    browser: Browser,
    headless: bool,
) -> ChromeWebDriver | FirefoxWebDriver:

    if browser is Browser.CHROME:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
    elif browser is Browser.FIREFOX:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    return driver


def get_cookie_path(cookie_dir: Path, browser: Browser) -> Path:
    return cookie_dir / browser.value / "cookies.pkl"


def save_cookies(driver: WebDriver, cookie_path: Path):
    # Ensure the directory exists before saving cookies
    cookie_path.parent.mkdir(parents=True, exist_ok=True)

    # Save cookies to the file
    with cookie_path.open("wb") as f:
        pickle.dump(driver.get_cookies(), f)
    logger.info(f"Cookies saved to {cookie_path}")


def load_cookies(driver: WebDriver, cookie_path: Path):
    if cookie_path.exists():
        with cookie_path.open("rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logger.info("Cookies restored!")
        driver.refresh()
    else:
        logger.info(f"No cookies file found at {cookie_path}")


def clear_cookies(cookie_path: Path):
    if cookie_path.exists():
        cookie_path.unlink()
        logger.info(f"Cookies cleared from {cookie_path}")
    else:
        logger.info(f"No cookies file found at {cookie_path}")
