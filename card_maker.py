import click
from rich.table import Table
from rich.console import Console

from scrape_conjugation import get_conjugations, minimal_tenses
from anki_ops import add_notes, list_existing_tags

# TODO: remove
temp = {'Indicativo Presente': [' io volo', ' tu voli', ' lei/lui vola', ' noi voliamo', ' voi volate', ' loro volano'], 'Indicativo Imperfetto': [' io volavo', ' tu volavi', ' lei/lui volava', ' noi volavamo', ' voi volavate', ' loro volavano'], 'Indicativo Futuro semplice': [' io volerò', ' tu volerai', ' lei/lui volerà', ' noi voleremo', ' voi volerete', ' loro voleranno'], 'Indicativo Passato prossimo': [' io ho volato', ' tu hai volato', ' lei/lui ha volato', ' noi abbiamo volato', ' voi avete volato', ' loro hanno volato', '', ' io sono volato', ' tu sei volato', ' lui è volato', ' lei è volata', ' noi siamo volati', ' voi siete volati', ' loro sono volati', ' loro sono volate']}

cardsets = {
    0: {
        'Indicativo Presente': ['io'],
        'Indicativo Passato prossimo': ['io']
    },
    1: {
        'Indicativo Presente': ['io', 'tu'],
        'Indicativo Imperfetto': ['io'],
        'Indicativo Futuro semplice': ['io'],
        'Indicativo Passato prossimo': ['io']
    },
    2: {
        'Indicativo Presente': ['io', 'tu', 'lei/lui', 'noi', 'voi', 'loro'],
        'Indicativo Imperfetto': ['io'],
        'Indicativo Futuro semplice': ['io'],
        'Indicativo Passato prossimo': ['io', 'noi']
    }
}

it_en_people = {
    "io": "I",
    "tu": "you",
    "lei/lui": "she/he",
    "noi": "we",
    "voi": "ya'll",
    "loro": "they"
}


def get_for_tense_person(tense: str, person: str, conjugations: dict) -> dict:
    """
    Given a tense and a person, return the conjugation for that person
    """
    occurrences = []
    peeps = conjugations[tense]
    for peep in peeps:
        # determine if there's essere and avere
        if tense == "Indicativo Passato prossimo" and person in peep:
            occurrences.append(peep)
        elif person in peep:
            return peep
    
    return ", ".join(occurrences)


def cardset_to_basic_card_format(infinitive: str, conjugations: dict, df: str, cardset: dict) -> list[dict]:
    cards = []

    for tense, persons in cardset.items():
        for person in persons:
            card = {
                "deckName": "Italiano",
                "modelName": "Basic",
                "fields": {
                    # later can try to get the english conjugation and put it on the front
                    "Front": f"{tense}: {it_en_people[person]} {df}", 
                    "Back": get_for_tense_person(tense, person=person, conjugations=conjugations)
                },
                "tags": [
                    "italiano_utils",
                    "itutils:v0.0",
                    infinitive,
                ]
            }
            cards.append(card)
    return cards


def print_cardset_data(vc: dict):
    print()
    for tense, persons in cardsets[2].items():
        table = Table(title=tense)
        table.add_column("Person", no_wrap=True)
        table.add_column("Conjugation", no_wrap=True)
        table.add_column("Cardsets", no_wrap=True)
        for person in persons: 

            in_cardsets = "2"
            if person in cardsets[1].get(tense, []):
                in_cardsets = "1, " + in_cardsets
            if person in cardsets[0].get(tense, []):
                in_cardsets = "0, " + in_cardsets

            table.add_row(person, get_for_tense_person(tense, person, vc), in_cardsets)

        console = Console()
        console.print(table)
    print()


def iteractive():
    # infinitive = "volare"
    # vc = temp
    # df = "to fly"

    infinitive = click.prompt("What's the verb infinitivo?", type=str)
    vc, df = get_conjugations(infinitive, minimal_tenses, withDef=True)

    print_cardset_data(vc)    

    cardset_num = click.prompt("Which cardset would you like to use?", type=int)

    cardlist = cardset_to_basic_card_format(infinitive, vc, df, cardsets[cardset_num])

    tags = set()
    for card in cardlist:
        tags.update(card["tags"])

    already_exists = list_existing_tags(list(tags))
    continue_anyway = click.confirm(f"Tags {already_exists} already exist. Continue anyway?")

    if not continue_anyway:
        print("Exiting")
        return 
    
    ids = add_notes(cardlist)
    print(ids)
                                        







if __name__ == "__main__":
    iteractive()
    