import enum
import math
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
# import argparse
from colorama import Fore, init

import image
import os
import re
from urllib.parse import urlparse

# Initialize colorama
init(autoreset=True)
# parser = argparse.ArgumentParser(description="Script para dar bypass em CAPTCHA.")
# parser.add_argument("--driver-path", required=True, help="Caminho do driver do navegador.")

# args = parser.parse_args()

DRIVER_PATH = r"C:\Users\Shiro\Documents\GitHub\auto-RTC\Driver\webdriver.exe"


USERNAME = "KaremM.Teresina"
PASSWORD = "BYD@2022"

HOME_PAGE="https://uscrm.byd.com/login"

print(f"{Fore.YELLOW}Iniciando o navegador...")

options = Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

DRIVER = webdriver.Firefox(service=Service(DRIVER_PATH), options=options)
DRIVER.maximize_window()
DRIVER.get(HOME_PAGE)
print(f"{Fore.GREEN}Navegador iniciado e página Inicial Carregada!")

class Condition(enum.Enum):
    CLICKABLE = "clickable"
    PRESENCE = "presence"
    NO_WAIT = "no_wait"

def get_element(cond, by, value, timeout=30, returnError=False):
    try:
        TIMEOUT=timeout
        if cond == Condition.CLICKABLE:
            return WebDriverWait(DRIVER, TIMEOUT).until(EC.element_to_be_clickable((by, value)))
        elif cond == Condition.PRESENCE:
            return WebDriverWait(DRIVER, TIMEOUT).until(EC.presence_of_element_located((by, value)))
        elif cond == Condition.NO_WAIT:
            return DRIVER.find_element(by, value)
    except Exception as e:
        print(f"{Fore.RED}Erro ao localizar o elemento: {value} - {str(e)}")
        if returnError:
            return None
        raise e

def refresh_page():
    print(f"{Fore.YELLOW}Atualizando a página...")
    DRIVER.refresh()
    wait_page_ready()

def wait_page_ready():
    WebDriverWait(DRIVER, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")


def login(username, password):
    print(f"{Fore.YELLOW}Iniciando o processo de login...")
    
    username_field = get_element(Condition.PRESENCE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[2]/div/div/input")

    password_field = get_element(Condition.PRESENCE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[4]/div/div/input")

    username_field.click()
    username_field.send_keys(username)
    password_field.click()
    password_field.send_keys(password)

    accept_cookies = get_element(Condition.CLICKABLE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[6]/div[1]/div/div[2]/button[3]")
    accept_cookies.click()
    
    read_politics = get_element(Condition.CLICKABLE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[5]/div/label/label")
    read_politics.click()
 
    login_button = get_element(Condition.CLICKABLE, By.XPATH, "//*[@id='msp']/div[1]/div/div/div[1]/div[2]/div/div[2]/form/div[5]/div/button")
    login_button.click()
    print(f"{Fore.GREEN}Credenciais enviadas.")
    
    
def get_image():
    print(f"{Fore.YELLOW}Capturando imagem do CAPTCHA...")
    captcha_image = get_element(Condition.PRESENCE, By.XPATH, "/html/body/div/div[1]/div/div/div[1]/div[4]/div/div[2]/div/div[1]/div/img")
    image_src = captcha_image.get_attribute("src")
    print(f"{Fore.GREEN}Imagem do CAPTCHA capturada.")
    return image_src, captcha_image

def resolve_captcha(x_pixel, image_width, image_element):
    """
    Move o slider do CAPTCHA até a posição x_pixel dentro da imagem.
    
    x_pixel: coordenada horizontal dentro da imagem (em pixels)
    image_element: elemento Selenium da imagem do CAPTCHA
    """
    print(f"{Fore.YELLOW}Iniciando a resolução do CAPTCHA...")

    # Pega o slider
    slider = get_element(
        Condition.CLICKABLE,
        By.XPATH,
        "/html/body/div/div[1]/div/div/div[1]/div[4]/div/div[2]/div/div[2]/div/div"
    )
    
    slider_width = slider.size['width']
    print(f"{Fore.MAGENTA}Largura do slider: {Fore.RED}{slider_width}{Fore.MAGENTA} pixels")
 
 
 
    real_width = image_element.size['width']
    print(f"{Fore.MAGENTA}Largura da imagem: {Fore.RED}{image_width}{Fore.MAGENTA} pixels")
    print(f"{Fore.MAGENTA}Largura mostrada na tela: {Fore.RED}{real_width}{Fore.MAGENTA} pixels")

    # Calcula a proporção entre a largura real e a largura mostrada
    scale_factor = real_width / image_width
    print(f"{Fore.MAGENTA}Fator de escala: {Fore.RED}{scale_factor}{Fore.MAGENTA}")
    # Ajusta a coordenada x_pixel de acordo com a escala
    print(f"{Fore.BLUE}Coordenada X original do CAPTCHA: {Fore.RED}{x_pixel}{Fore.BLUE} pixels")
    x_pixel = int(x_pixel * scale_factor)
    print(f"{Fore.BLUE}Coordenada X ajustada do CAPTCHA: {Fore.RED}{x_pixel}{Fore.BLUE} pixels")

    offset_x = x_pixel - (slider_width // 2)  # Centraliza o clique no meio do slider
    print(f"{Fore.MAGENTA}Calculando deslocamento do slider: {Fore.RED}{offset_x}{Fore.MAGENTA} pixels")
    
    
    
    
    # Movimenta o slider
    action = ActionChains(DRIVER)
    action.click_and_hold(slider).perform()
    sleep(0.2)
    # action.move_to_element(image_element).perform()
    # sleep(0.2)
    action.move_by_offset(offset_x, 0).perform()
    action.release().perform()

    
    
    
    print(f"Slider movido aproximadamente {Fore.RED}{offset_x}{Fore.RESET} pixels para a direita.")

login(USERNAME, PASSWORD)
image_src, image_element = get_image()
x, width = image.get_image_x_y(image_src, debug=True)
if x is None:
    exit(1)
print(f"{Fore.CYAN}Coordenada X da peça do CAPTCHA: {x}")
resolve_captcha(x, width, image_element)