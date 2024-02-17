from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


minimal_tenses = [
    "Indicativo Presente",
    "Indicativo Imperfetto",
    "Indicativo Futuro semplice",
    "Indicativo Passato prossimo",
]


def _get_tense_options(verb: str) -> list[str]:
    """
    Find all elements with a 'mobile-title' attribute
    Can be used for populating tenses to fetch conjugations for
    """
    driver = _setup_driver(verb)
    elements_with_mobile_title = driver.find_elements(By.XPATH, "//*[@mobile-title]")
    
    out = []
    for element in elements_with_mobile_title:
        out.append(element.get_attribute("mobile-title"))
    
    driver.quit()
    return out


def get_definitions(verb: str, driver=None) -> str:
    if driver is None:
        driver = _setup_driver(verb)

    translation_element = driver.find_element(By.ID, "list-translations")
    translation = translation_element.find_element(By.XPATH, value="//p[@class='context-term']")
    translation = WebDriverWait(driver, 10).until(
       EC.visibility_of_element_located((By.XPATH, "//p[@class='context-term']"))
    )

    out = translation.text
    driver.quit()
    return out


def get_conjugations(verb: str, tenses: list[str], withDef=False) -> dict:
    """build a dict of conjugations for the minimal tenses"""
    driver = _setup_driver(verb)
    
    out = {}
    for tense in tenses:
        out[tense] = []
        try:
            # Locate the section by its mobile-title attribute
            tense_section = driver.find_element(By.XPATH, f"//div[@mobile-title='{tense}']")
            pairs = tense_section.find_elements(By.XPATH, ".//li")
            print(f"{tense_section.get_attribute('mobile-title')}: {len(pairs)}")

            for li in pairs:
                i_tags = li.find_elements(By.XPATH, ".//i")

                row_text = ""
                for i in i_tags:
                    row_text += " " + i.text
                out[tense].append(row_text.strip())

        except Exception as e:
            print(e)
            print(f"Could not find tense {tense}")
            raise e
    
    definitions = ""
    if withDef:
       definitions = get_definitions(verb, driver=driver)

    driver.quit()
    return (out, definitions)


def _setup_driver(verb: str) -> webdriver.Firefox:
    options = Options()
    options.page_load_strategy = 'eager'
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://conjugator.reverso.net/conjugation-italian-verb-{verb}.html")
    return driver


if __name__ == "__main__":
    vc, defs = get_conjugations("volare", minimal_tenses, True)

    print(vc)
    print(defs)
    # definitions = get_definitions("volare")
    # print(definitions)

    