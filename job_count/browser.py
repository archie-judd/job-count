import logging
import pickle
import shutil
from enum import StrEnum
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver

logger = logging.getLogger(__name__)

WebDriver = ChromeWebDriver | FirefoxWebDriver

DEFAULT_COOKIE_DIR = Path("~/.local/share/job-count").expanduser()


class Browser(StrEnum):
    CHROME = "chrome"
    FIREFOX = "firefox"


def make_driver(
    browser: Browser,
    headless: bool,
) -> ChromeWebDriver | FirefoxWebDriver:

    try:
        match browser:
            case Browser.CHROME:
                options = ChromeOptions()
                if headless:
                    options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)
            case Browser.FIREFOX:
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                driver = webdriver.Firefox(options=options)
            case _:
                raise ValueError(f"Unsupported browser: {browser}")
    except Exception as e:
        raise e
        logger.error(
            f"{browser.value} could not be opened. Ensure the it is installed or select "
            "another browser using the --browser argument. Available browsers: "
            f"{', '.join(list(Browser))}. Error: {e}"
        )
        exit(1)
    return driver


def get_cookie_path(cookie_dir: Path, browser: Browser) -> Path:
    return cookie_dir / browser.value / "cookies.pkl"


def save_cookies(driver: WebDriver, cookie_path: Path):
    cookie_path.parent.mkdir(parents=True, exist_ok=True)

    with cookie_path.open("wb") as f:
        pickle.dump(driver.get_cookies(), f)
    logger.info(f"Cookies saved to {cookie_path}")


def load_cookies(driver: WebDriver, cookie_path: Path) -> bool:
    if cookie_path.exists():
        with cookie_path.open("rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        logger.info("Cookies restored!")
        driver.refresh()
        return True
    else:
        logger.error(
            f"No cookies file found at {cookie_path}. Run the login command first."
        )


def clear_cookies(cookie_path: Path):
    if cookie_path.exists():
        cookie_path.unlink()
        logger.info(f"Cookies cleared from {cookie_path}")
    else:
        logger.info(f"No cookies file found at {cookie_path}")
