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


def init_driver(remote="http://localhost:4444"):
    """Init a Chrome remote driver

    Args:
        dataFolder (str, optional): Folder path where store browser files. Defaults to "./userData".
        remote (str, optional): Remote selenium chrome. Defaults to "./userData".
    Returns:
        (RemoteWebDriver): Driver to control the browser
    """
    options = webdriver.ChromeOptions()
    options.set_capability("se:name", "Survey sender")
    options.add_argument("--user-data-dir=/home/seluser/userData")

    driver = webdriver.Remote(
        command_executor=f'{remote}/wd/hub',
        options=options
    )

    print("Created driver")

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


def send_survey(driver, survey, remote):
    """Sends a survey to whatsapp

    Args:
        driver (RemoteWebDriver): Driver to control the browser
        survey (file): Survey configuration to send to whatsapp
    """
    survey = json.load(survey)

    driver.get('https://web.whatsapp.com')

    if not driver.find_elements(By.XPATH, '//*[@title="Chats"]'):
        print(f"Login needed! Enter into {remote}/ui/#/sessions")

        try:
            wait_for_element(driver, (By.XPATH, '//*[@title="Chats"]'), 180)
            print("Loged!!!")
        except TimeoutException:
            print("Loading took too much time!")

    print("Searching group")
    # Locate and interact with the search box to find the group
    search_box = wait_for_element(
        driver, (By.XPATH, '//div[@contenteditable="true" and @data-tab="3"]'), timeout=20)
    search_box.clear()
    search_box.send_keys(survey["group"])
    search_box.send_keys(Keys.ENTER)

    print("Creating survey")
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
    driver = init_driver(params.remote)

    for survey in params.surveyFiles:
        try:
            send_survey(driver, survey, params.remote)
        finally:
            driver.quit()

    print("Finished OK!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='whatsapp_survey_sender',
        description='Send surveis to chats in whatsapp. Made with python and selenium')

    parser.add_argument("surveyFiles",
                        type=argparse.FileType('r', encoding="UTF8"),
                        nargs='+',
                        help="Json file with survey configuration")
    parser.add_argument("-r", "--remote",
                        dest="remote",
                        help="Remote Selenium browser. E.g. http://localhost:4444",
                        default="http://localhost:4444")
    args = parser.parse_args()

    main(args)
