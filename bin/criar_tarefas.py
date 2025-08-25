import enum
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import argparse

parser = argparse.ArgumentParser(description="Script para automação de tarefas no RTC.")
parser.add_argument("--ib", required=True, help="Número do IB.")
parser.add_argument("--user", required=True, help="Usuário para login.")
parser.add_argument("--password", required=True, help="Senha para login.")
parser.add_argument("--driver-path", required=True, help="Caminho do driver do navegador.")

args = parser.parse_args()

IB = args.ib.strip()
USER = args.user.strip()
PASSWORD = args.password.strip()
DRIVER_PATH = args.driver_path.strip()

print(f"IB: {IB}")
print(f"Usuário: {USER}")
print(f"Senha: {'*' * len(PASSWORD)}")

T1 = f"1 - Análise de Impacto ({IB})"
T2 = f"2 - Realizar Mensuração Estimada ({IB})"
T3 = f"3 - Elaborar Requisito ({IB})"
T4 = f"4 - Realizar Mensuração Detalhada ({IB})"
T5 = f"5 - Estruturar Testes ({IB})"
T6 = f"6 - Codificar Programa ({IB})"
T7 = f"7 - Executar Testes ({IB})"
T8 = f"Aprovar Requisito ({IB})"

HOME_PAGE="https://gid.caixa:9443/ccm/web/projects/Comunidade%20C%C3%A2mbio,%20Investimentos%20e%20Mercado%20de%20Capitais#action=com.ibm.team.dashboard.viewDashboard&team=CI030%20-%20Fundos%20de%20investimentos%20(SIART_SIGPB%20-%20RJE)"

DRIVER = webdriver.Firefox(service=Service(DRIVER_PATH))
DRIVER.maximize_window()
DRIVER.get(HOME_PAGE)

class Condition(enum.Enum):
    CLICKABLE = "clickable"
    PRESENCE = "presence"
    NO_WAIT = "no_wait"

def get_element(cond, by, value):
    TIMEOUT=30
    if cond == Condition.CLICKABLE:
        return WebDriverWait(DRIVER, TIMEOUT).until(EC.element_to_be_clickable((by, value)))
    elif cond == Condition.PRESENCE:
        return WebDriverWait(DRIVER, TIMEOUT).until(EC.presence_of_element_located((by, value)))
    elif cond == Condition.NO_WAIT:
        return DRIVER.find_element(by, value)

def refresh_page():
    DRIVER.refresh()
    wait_page_ready()

def wait_page_ready():
    WebDriverWait(DRIVER, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

def select_option(XPATH, text):
    field = get_element(Condition.PRESENCE, By.XPATH, XPATH)
    field.click()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(text).perform()
    sleep(0.6)
    ActionChains(DRIVER).send_keys(Keys.RETURN).perform()

def login(user, password):
    login_element = get_element(Condition.PRESENCE, By.ID, "jazz_app_internal_LoginWidget_0_userId")
    password_element = get_element(Condition.PRESENCE ,By.ID, "jazz_app_internal_LoginWidget_0_password")
    # Preencher login e senha
    login_element.send_keys(user)
    password_element.send_keys(password)
    login_button = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "button.j-button-primary[type='submit']")
    login_button.click()

def search_ib(ib):
    # Preencher o campo de busca com IB
    search_input = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "input.SearchInputText[role='search']")
    search_input.send_keys(ib)
    search_input.send_keys(Keys.RETURN)
    refresh_page()

def get_desc():
    description_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "div.RichTextEditorWidget[aria-label='Descrição']")
    description_html = description_element.get_attribute("innerHTML")
    description_html = description_html.replace("<strong>", "").replace("</strong>", "").replace("<br/>", "\n").replace("<br>", "\n")
    soup = BeautifulSoup(description_html, "html.parser")
    description_text = soup.get_text(separator="\n")
    return description_text

def get_gestor():
    created_by_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "a.jazz-ui-ResourceLink[aria-label^='Criado Por']")
    return created_by_element.get_attribute("aria-label").replace("Criado Por ", "")

def create_child_task():
    # Esperar pelo elemento da aba "Links" e clicar nela
    links_tab = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[2]/div/div[2]/a[7]")
    links_tab.click()
    # Esperar pelo dropdown de ações e clicar nele
    refresh_page()
    dropdown = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/div[3]/div/div/div/div/div[1]/div/div[2]/span[2]")
    dropdown.click()
    # item "Incluir filhos" e clicar nele
    inc_filhos_div = get_element(Condition.NO_WAIT, By.XPATH, "(//tr[@aria-label='Incluir Filhos '])[last()]")
    inc_filhos_id = inc_filhos_div.get_attribute("id")
    inc_filhos = get_element(Condition.NO_WAIT, By.ID, inc_filhos_id + "_text")
    if inc_filhos.is_displayed():
        dropdown.click()
        DRIVER.execute_script("arguments[0].scrollIntoView(true);", inc_filhos)
        inc_filhos.click()

    # Esperar pelo select de tipo de filho
    select_tarefa = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "select.selectSelect[aria-label='Tipo']")
    select_tarefa.click()
    # Selecionar a opção "Tarefa"
    task_option = get_element(Condition.CLICKABLE, By.XPATH, "//option[@value='task' and text()='Tarefa']")
    task_option.click()
    # Esperar pelo campo de criar uma nova tarefa
    criar_tarefa = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "a.CreateItemAnchor[title='Criar o Tarefa vinculado na área do projeto Comunidade Câmbio, Investimentos e Mercado de Capitais']")
    criar_tarefa.click()

def fill_title(title):
    num =  3
    title_input = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/div[2]")
    wait_page_ready()
    ActionChains(DRIVER).move_to_element(title_input).click().perform()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(title).perform()

def fill_gestor():
    num = 3
    select_option(
        f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[1]/div/table/tbody/tr[9]/td/div/div[2]",
        GESTOR
    )

def fill_group():
    num = 3
    select_option(
        
        f'/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[2]/td/div/div[2]',
        'Não'
    )

def fill_description():
    description_field = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "div.RichTextEditorWidget[aria-label='Descrição']")
    DRIVER.execute_script("arguments[0].scrollIntoView();", description_field)
    wait_page_ready()
    ActionChains(DRIVER).move_to_element(description_field).click().perform()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(DESC).perform()

def select_current_date():
    num = 3
    dropdown_element = get_element(Condition.PRESENCE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[4]/td/div/div[2]/a[2]")
    ActionChains(DRIVER).move_to_element(dropdown_element).click().perform()
    ActionChains(DRIVER).send_keys(Keys.RETURN).perform()

def select_one_week_later():
    num = 3
    dropdown_element = get_element(Condition.PRESENCE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[5]/td/div/div[2]/a[2]")
    ActionChains(DRIVER).move_to_element(dropdown_element).click().perform()
    ActionChains(DRIVER).send_keys(Keys.ARROW_DOWN).send_keys(Keys.SPACE).send_keys(Keys.RETURN).perform()

def salvar_tarefa():
    num = 3
    DRIVER.execute_script("window.scrollTo(0, 0);")
    save_button = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[1]/div[1]/span/span[3]/span/button[2]")
    save_button.click()
    sleep(0.1)
    WebDriverWait(DRIVER, 30).until(
        lambda driver: driver.execute_script(
            "return window.getComputedStyle(document.querySelector('div.status-message'), null).display"
        ) == "none"
    )

login(USER, PASSWORD)


search_ib(IB)
DESC = get_desc()
GESTOR = get_gestor()


create_child_task() # analize de impacto
fill_title(T1)
fill_gestor()
fill_group()
select_current_date()
select_one_week_later()
fill_description()
salvar_tarefa()


arr = [T2, T3, T4, T5, T6, T7, T8]
for T in arr:
    search_ib(IB)
    create_child_task()
    fill_title(T)
    fill_gestor()
    fill_group()
    select_current_date()
    salvar_tarefa()
