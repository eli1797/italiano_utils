import time
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


def get_definitions(verb: str, driver=None) -> str:
    if driver is None:
        driver = setup_driver(verb)
    try:
        translation = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//p[@class='context-term']"))
        )
        out = translation.text
    except Exception as e:
        print(f"Error getting definitions: {e}")
        out = ""
    finally:
        if driver is None:
            driver.quit()

    return out


def get_gerundio(verb: str, driver=None) -> str:
    """Scrape the gerundio form of the given verb"""
    if driver is None:
        driver = setup_driver(verb)
    
    try:
        # Find the Gerundio section
        gerundio_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@mobile-title='Gerundio Presente']"))
        )
        
        # Find the verb form within the Gerundio section
        gerundio_form = gerundio_section.find_element(By.XPATH, ".//li/i[@class='verbtxt']")
        
        return gerundio_form.text
    except Exception as e:
        print(f"Error getting gerundio form: {e}")
        return ""
    finally:
        if driver is None:
            driver.quit()


def get_conjugations(verb: str, tenses: list[str], withDef=False, withGr=False, driver=None) -> dict:
    """build a dict of conjugations for the minimal tenses"""
    if driver is None:
        driver = setup_driver(verb)

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

    gr = ""
    if withGr:
        gr = get_gerundio(verb, driver=driver)

    driver.quit()
    return (out, definitions, gr)


def handle_gdpr_popup(driver):
    try:
        # Wait for the "Agree and close" button to be clickable
        agree_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        # Click the button
        agree_button.click()
        print("GDPR popup handled successfully")
    except Exception as e:
        print(f"Failed to handle GDPR popup: {e}")


def setup_driver(verb: str) -> webdriver.Firefox:
    options = Options()
    options.page_load_strategy = 'eager'
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(f"https://conjugator.reverso.net/conjugation-italian-verb-{verb}.html")

    handle_gdpr_popup(driver=driver)
    return driver


if __name__ == "__main__":
    vc, defs = get_conjugations("volare", minimal_tenses, True)

    print(vc)
    print(defs)
    # definitions = get_definitions("volare")
    # print(definitions)

    