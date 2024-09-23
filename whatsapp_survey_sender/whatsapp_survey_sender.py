"""Sends surveys from whatsapp
"""
import json
import os.path
import argparse
import time
import jsonata
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


def init_edge_driver(data_folder, gui):
    """Init a Edge driver

    Args:
        dataFolder (str): Folder path where store browser files.
        gui (bool): True to open a browser window.

    Returns:
        (RemoteWebDriver): Driver to control the browser
    """
    options = webdriver.EdgeOptions()
    options.add_argument(f"user-data-dir={os.path.abspath(data_folder)}")

    if not gui:
        print("Starting Edge headless mode!")
        options.use_chromium = True
        options.add_argument("--headless=new")

    driver = webdriver.Edge(options=options)
    return driver


def init_chrome_driver(data_folder, gui):
    """Init a Chrome driver

    Args:
        dataFolder (str): Folder path where store browser files.
        gui (bool): True to open a browser window.

    Returns:
        (RemoteWebDriver): Driver to control the browser
    """
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={os.path.abspath(data_folder)}")

    if not gui:
        print("Starting Chrome headless mode!")
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    return driver


def init_driver(data_folder="./userData", gui=False, browser="chrome"):
    """Initializes selenium driver

    Args:
        dataFolder (str, optional): Folder path where store browser files. Defaults to "./userData".
        gui (bool, optional): True to open a browser window. Defaults to False.
        browser (str, optional): Browser to use in selenium. Defaults to chrome

    Returns:
        (RemoteWebDriver): Driver to control the browser
    """
    match browser:
        case "chrome":
            driver = init_chrome_driver(data_folder, gui)
        case "edge":
            driver = init_edge_driver(data_folder, gui)

    driver.implicitly_wait(10)
    return driver


def wait_for_element(driver, element_filter, timeout=30):
    """Waits for a element to be available

    Args:
        filter (tuple): How to search the element
        timeout (int, optional): Waiting time until error. Defaults to 30.

    Returns:
        WebDriverWait: Element once is found
    """
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(element_filter))


def send_survey(driver, survey):
    """Sends a survey to whatsapp

    Args:
        driver (RemoteWebDriver): Driver to control the browser
        survey (file): Survey configuration to send to whatsapp
    """
    survey = json.load(survey)

    driver.get('https://web.whatsapp.com')

    if not driver.find_elements(By.XPATH, '//*[@title="Chats"]'):
        try:
            wait_for_element((By.XPATH, '//*[@title="Chats"]'), 180)
            print("Loged!!!")
        except TimeoutException:
            print("Loading took too much time!")

    # Locate and interact with the search box to find the group
    search_box = wait_for_element(
        driver, (By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'), timeout=10)
    search_box.clear()
    search_box.send_keys(survey["group"])
    search_box.send_keys(Keys.ENTER)

    # Find the message box and send the message
    attach_button_xpath = (
        By.XPATH, '//div[@aria-label="Adjuntar" and @data-tab="10"]')
    wait_for_element(driver, attach_button_xpath, timeout=10).click()

    survey_button_xpath = (By.XPATH, '//span[text()="Encuesta"]')
    wait_for_element(driver, survey_button_xpath, timeout=10).click()

    action_chain = ActionChains(driver)

    if survey["jsonataName"]:
        action_chain.send_keys(jsonata.Jsonata("$eval(name)").evaluate(survey))
    else:
        action_chain.send_keys(survey["name"])

    action_chain.send_keys(Keys.TAB) \
        .send_keys(Keys.TAB)

    for option in survey["options"]:
        action_chain.send_keys(option) \
            .send_keys(Keys.TAB) \
            .send_keys(Keys.TAB)

    action_chain.send_keys(Keys.TAB) \
        .send_keys(Keys.TAB) \

    if not survey["multipleAnswers"]:
        action_chain.send_keys(Keys.ENTER)

    action_chain.send_keys(Keys.TAB).send_keys(Keys.ENTER)

    action_chain.perform()

    time.sleep(3)  # Wait until survey is done sending


def main(params):
    """Main execution

    Args:
        params (object): Object with program arguments
    """
    driver = init_driver(params.dataFolder, params.gui, params.browser)

    for survey in params.surveyFiles:
        send_survey(driver, survey)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='whatsapp_survey_sender',
        description='Send surveis to chats in whatsapp. Made with python and selenium')

    parser.add_argument("surveyFiles",
                        type=argparse.FileType('r', encoding="UTF8"),
                        nargs='+',
                        help="Json file with survey configuration")
    parser.add_argument("-b", "--browser",
                        default="chrome",
                        dest="browser",
                        help="Select the browser to use in Selenium",
                        choices=["chrome", "edge"])
    parser.add_argument("-g", "--gui",
                        action='store_true',
                        default=False,
                        dest="gui",
                        help="Show the browser window")
    parser.add_argument("--data_file",
                        default="./userData",
                        dest="dataFolder",
                        help="Place where store the broswer files")
    args = parser.parse_args()
    
    main(args)
