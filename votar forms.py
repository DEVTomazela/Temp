"""
Responde o Google Forms repetidamente em uma janela do Chrome ja aberta.

Instalacao:
    pip install selenium

Abra o Chrome com a porta de depuracao (feche as janelas antigas antes):
    Windows:
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\\chrome-forms
    macOS:
        /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-forms

Abra o forms nessa janela, faca login se necessario e execute:
    python votar_forms.py
"""

import time

from selenium import webdriver
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

TEXTO_RESPOSTA = "Tax Intelligence Hub"
TOTAL_ENVIOS = 10
PAUSA_SEGUNDOS = 1
TIMEOUT_SEGUNDOS = 20

XPATH_ENVIAR = (
    "//div[@role='button'][.//span[normalize-space()='Enviar' "
    "or normalize-space()='Submit']]"
)
XPATH_NOVA_RESPOSTA = (
    "//a[contains(., 'Responder novamente') "
    "or contains(., 'Enviar outra resposta') "
    "or contains(., 'Submit another response')]"
)


def clicar(driver, elemento):
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'}); arguments[0].click();",
        elemento,
    )


def achar_opcao(driver):
    alvo = TEXTO_RESPOSTA.lower()
    for opcao in driver.find_elements(
        By.CSS_SELECTOR, "[role='radio'], [role='checkbox']"
    ):
        try:
            texto = " ".join(
                [
                    opcao.get_attribute("aria-label") or "",
                    opcao.get_attribute("data-value") or "",
                ]
            ).lower()
        except StaleElementReferenceException:
            continue
        if alvo in texto:
            return opcao
    return False


def main():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, TIMEOUT_SEGUNDOS)

    for envio in range(1, TOTAL_ENVIOS + 1):
        try:
            clicar(driver, wait.until(achar_opcao))
            clicar(driver, wait.until(lambda d: d.find_element(By.XPATH, XPATH_ENVIAR)))
            link = wait.until(lambda d: d.find_element(By.XPATH, XPATH_NOVA_RESPOSTA))
            print(f"Envio {envio}/{TOTAL_ENVIOS} concluido")

            if envio < TOTAL_ENVIOS:
                clicar(driver, link)
                time.sleep(PAUSA_SEGUNDOS)
        except TimeoutException:
            print(f"Parei no envio {envio}: elemento nao encontrado a tempo.")
            print(f"URL atual: {driver.current_url}")
            break


if __name__ == "__main__":
    main()
