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
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

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


print(f"{Fore.GREEN}IB: {IB}")
print(f"{Fore.GREEN}Usuário: {USER}")
print(f"{Fore.GREEN}Senha: {'*' * len(PASSWORD)}")


T1 = f"1 - Análise de Impacto ({IB})"
T2 = f"2 - Realizar Mensuração Estimada ({IB})"
T3 = f"3 - Elaborar Requisito ({IB})"
T4 = f"4 - Realizar Mensuração Detalhada ({IB})"
T5 = f"5 - Estruturar Testes ({IB})"
T6 = f"6 - Codificar Programa ({IB})"
T7 = f"7 - Executar Testes ({IB})"
T8 = f"Aprovar Requisito ({IB})"

HOME_PAGE="https://gid.caixa:9443/ccm/web/projects/Comunidade%20Fundos%20de%20Investimento#action=com.ibm.team.dashboard.viewDashboard&team=CI030%20-%20Fundos%20de%20investimentos%20(SIART_SIGPB%20-%20RJE)"

print(f"{Fore.YELLOW}Iniciando o navegador...")
DRIVER = webdriver.Firefox(service=Service(DRIVER_PATH))
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

def select_option(XPATH, text):
    print(f"{Fore.YELLOW}Selecionando opção: {text}")
    field = get_element(Condition.PRESENCE, By.XPATH, XPATH)
    field.click()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(text).perform()
    sleep(0.6)
    ActionChains(DRIVER).send_keys(Keys.RETURN).perform()

def login(user, password):
    print(f"{Fore.YELLOW}Realizando login...")
    login_element = get_element(Condition.PRESENCE, By.ID, "jazz_app_internal_LoginWidget_0_userId")
    password_element = get_element(Condition.PRESENCE ,By.ID, "jazz_app_internal_LoginWidget_0_password")
    # Preencher login e senha
    login_element.send_keys(user)
    password_element.send_keys(password)
    login_button = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "button.j-button-primary[type='submit']")
    login_button.click()
    print(f"{Fore.GREEN}Login realizado com sucesso!")

def search_ib(ib):
    print(f"{Fore.YELLOW}Buscando IB: {ib}")
    # Preencher o campo de busca com IB
    search_input = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "input.SearchInputText[role='search']")
    search_input.send_keys(ib)
    search_input.send_keys(Keys.RETURN)
    refresh_page()

def get_desc():
    print(f"{Fore.YELLOW}Obtendo descrição...")
    description_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "div.RichTextEditorWidget[aria-label='Descrição']")
    description_html = description_element.get_attribute("innerHTML")
    description_html = description_html.replace("<strong>", "").replace("</strong>", "").replace("<br/>", "\n").replace("<br>", "\n")
    soup = BeautifulSoup(description_html, "html.parser")
    description_text = soup.get_text(separator="\n")
    print(f"{Fore.GREEN}Descrição obtida.")
    return description_text

def get_gestor():
    print(f"{Fore.YELLOW}Obtendo gestor...")
    created_by_element = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "a.jazz-ui-ResourceLink[aria-label^='Criado Por']")
    gestor = created_by_element.get_attribute("aria-label").replace("Criado Por ", "")
    print(f"{Fore.GREEN}Gestor obtido: {gestor}")
    return gestor

def drop_down_part():
    print(f"{Fore.YELLOW}Clicando no DropDown...")
    dropdown = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[2]/div/div[3]/div/div/div[2]/div[2]/div/div/div[3]/div/div/div/div/div[1]/div/div[2]/span[2]")
    dropdown.click()
    print(f"{Fore.GREEN}DropDown clicado!")
    print(f"{Fore.YELLOW}Selecionando a opção Incluir Filhos...")
    # item "Incluir filhos" e clicar nele
    inc_filhos_div = get_element(Condition.NO_WAIT, By.XPATH, "(//tr[@aria-label='Incluir Filhos '])[last()]")
    inc_filhos_id = inc_filhos_div.get_attribute("id")
    inc_filhos = get_element(Condition.NO_WAIT, By.ID, inc_filhos_id + "_text")
    if inc_filhos.is_displayed():
        dropdown.click()
        DRIVER.execute_script("arguments[0].scrollIntoView(true);", inc_filhos)
        inc_filhos.click()
    print(f"{Fore.GREEN}Opção Incluir Filhos selecionada!")

def task_part():
    print(f"{Fore.YELLOW}Selecionando tipo de tarefa filha...")
    select_tarefa = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "select.selectSelect[aria-label='Tipo']")
    select_tarefa.click()
    print(f"{Fore.GREEN}Tipo de tarefa filha selecionado!")
    print(f"{Fore.YELLOW}Selecionando a opção Tarefa...")
    # Selecionar a opção "Tarefa"
    task_option = get_element(Condition.CLICKABLE, By.XPATH, "//option[@value='task' and text()='Tarefa']")
    task_option.click()
    print(f"{Fore.GREEN}Opção Tarefa selecionada!")

def create_child_task():
    print(f"{Fore.YELLOW}Criando tarefa filha...")
    print(f"{Fore.YELLOW}Indo aba Links...")
    # Esperar pelo elemento da aba "Links" e clicar nela
    links_tab = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[2]/div/div[2]/a[7]")
    links_tab.click()
    print(f"{Fore.GREEN}Estamos na aba Links!")
    refresh_page()
    count = 0
    while get_element(Condition.NO_WAIT, By.CSS_SELECTOR, ".jazz-ui-modalunderlay-root", returnError=True, timeout=3) is None and count <= 5:
        drop_down_part()
        count += 1
    task_part()
    print(f"{Fore.YELLOW}Clicando em Criar Tarefa...")
    # Esperar pelo campo de criar uma nova tarefa
    criar_tarefa = get_element(Condition.PRESENCE, By.CSS_SELECTOR, "a.CreateItemAnchor[title='Criar o Tarefa vinculado na área do projeto Comunidade Fundos de Investimento']")
    criar_tarefa.click()
    print(f"{Fore.GREEN}Tarefa filha criada com sucesso!")

def fill_title(title):
    print(f"{Fore.YELLOW}Preenchendo o título: {title}")
    num =  3
    title_input = get_element(Condition.CLICKABLE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[1]/div[2]/div[1]/div[3]/div[2]/div/div/div[2]")
    wait_page_ready()
    ActionChains(DRIVER).move_to_element(title_input).click().perform()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(title).perform()
    print(f"{Fore.GREEN}Título preenchido.")

def fill_gestor():
    print(f"{Fore.YELLOW}Preenchendo o gestor: {GESTOR}")
    num = 3
    select_option(
        f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[1]/div/table/tbody/tr[9]/td/div/div[2]",
        GESTOR
    )
    print(f"{Fore.GREEN}Gestor preenchido.")

def fill_group():
    print(f"{Fore.YELLOW}Preenchendo o grupo: Não")
    num = 3
    select_option(
        
        f'/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[2]/td/div/div[2]',
        'Não'
    )
    print(f"{Fore.GREEN}Grupo preenchido.")

def fill_description():
    print(f"{Fore.YELLOW}Preenchendo a descrição...")
    description_field = get_element(Condition.CLICKABLE, By.CSS_SELECTOR, "div.RichTextEditorWidget[aria-label='Descrição']")
    DRIVER.execute_script("arguments[0].scrollIntoView();", description_field)
    wait_page_ready()
    ActionChains(DRIVER).move_to_element(description_field).click().perform()
    sleep(0.5)
    ActionChains(DRIVER).send_keys(DESC).perform()
    print(f"{Fore.GREEN}Descrição preenchida.")

def select_current_date():
    print(f"{Fore.YELLOW}Selecionando a data atual...")
    num = 3
    dropdown_element = get_element(Condition.PRESENCE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[4]/td/div/div[2]/a[2]")
    ActionChains(DRIVER).move_to_element(dropdown_element).click().perform()
    ActionChains(DRIVER).send_keys(Keys.RETURN).perform()
    print(f"{Fore.GREEN}Data atual selecionada.")

def select_one_week_later():
    print(f"{Fore.YELLOW}Selecionando a data uma semana depois...")
    num = 3
    dropdown_element = get_element(Condition.PRESENCE, By.XPATH, f"/html/body/div[1]/div/table/tbody/tr[1]/td[2]/div[2]/div/div[1]/div[3]/div/div[{num}]/div/div[3]/div/div/div/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[1]/td[2]/div/table/tbody/tr[5]/td/div/div[2]/a[2]")
    ActionChains(DRIVER).move_to_element(dropdown_element).click().perform()
    ActionChains(DRIVER).send_keys(Keys.ARROW_DOWN).send_keys(Keys.SPACE).send_keys(Keys.RETURN).perform()
    print(f"{Fore.GREEN}Data uma semana depois selecionada.")

def salvar_tarefa():
    print(f"{Fore.YELLOW}Salvando a tarefa...")
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
    print(f"{Fore.GREEN}Tarefa salva com sucesso!")

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
