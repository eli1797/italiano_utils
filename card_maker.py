import click
import random
from rich.table import Table
from rich.console import Console

from scrape_conjugation import get_conjugations, minimal_tenses
from anki_ops import add_notes, list_existing_tags


"""
TODO:
- maybe: add the gerund, at least as an option to include it
- add audio recognition card of the infinitive, maybe others if irregular?
  - how can recognize if irregular? scrapable or just recognizable probably

"""

cardsets = {
    0: {},
    1: {
        'Indicativo Presente': ['io'],
        'Indicativo Passato prossimo': ['io']
    },
    2: {
        'Indicativo Presente': ['io', 'tu', 'lei/lui'],
        'Indicativo Passato prossimo': ['io']
    },
    3: {
        'Indicativo Presente': ['io', 'tu', 'lei/lui', 'noi', 'voi', 'loro'],
        'Indicativo Imperfetto': ['io'],
        'Indicativo Futuro semplice': ['io'],
        'Indicativo Passato prossimo': ['io', 'noi']
    },
    4: {
        'Indicativo Presente': [random.choice(['io', 'tu', 'lei/lui', 'noi', 'voi', 'loro'])],
        'Indicativo Imperfetto': [random.choice(['io', 'tu', 'lei/lui', 'noi', 'voi', 'loro'])],
        'Indicativo Futuro semplice': [random.choice(['io', 'tu', 'lei/lui', 'noi', 'voi', 'loro'])],
        'Indicativo Passato prossimo': [random.choice(['io', 'noi'])]
    },
}

scraped_anki_tenses = {
    "Indicativo Presente": "presente",
    "Indicativo Imperfetto": "imperfetto",
    "Indicativo Passato prossimo": "passato_prossimo",
    "Indicativo Futuro semplice": "futuro",
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
        if tense == "Indicativo Passato prossimo" and (person + " ") in peep:  # the space is to avoid matching "io" with "giocare" etc.
            occurrences.append(peep)
        elif person in peep:
            return peep
    
    return ", ".join(occurrences)


def cardset_to_basic_card_format(infinitive: str, conjugations: dict, df: str, cardset: dict, it_first = False) -> list[dict]:
    fields = {
                "Front": df, 
                "Back": infinitive,
    }
    if it_first: 
        fields = {
            "Front": infinitive,
            "Back": df,
        }

    cards = [
        {
            "deckName": "Italiano",
            "modelName": "Basic",
            "fields": fields,
            "tags": [
                "italiano_utils",
                "itutils:v0.0",
                "infinito",
                infinitive,
            ]
        }
    ]

    for tense, persons in cardset.items():
        for person in persons:
            fields = {
                    "Front": f"{tense}: {it_en_people[person]} {df}", 
                    "Back": get_for_tense_person(tense, person=person, conjugations=conjugations)
            }
            if it_first: 
                fields = {
                    "Front": get_for_tense_person(tense, person=person, conjugations=conjugations),
                    "Back": f"{tense}: {it_en_people[person]} {df}",
                }
            card = {
                "deckName": "Italiano",
                "modelName": "Basic",
                "fields": fields,
                "tags": [
                    "italiano_utils",
                    "itutils:v0.0",
                    infinitive,
                    scraped_anki_tenses.get(tense, "")
                ]
            }
            cards.append(card)

    return cards


def print_cardset_data(infinitive: str, vc: dict, df: str, gr: str):
    print()
    for tense, persons in cardsets[3].items():
        table = Table(title=tense)
        table.add_column("Person", no_wrap=True)
        table.add_column("Conjugation", no_wrap=True)
        table.add_column("Cardsets", no_wrap=True)
        for person in persons: 

            in_cardsets = "4?"
            if person in cardsets[3].get(tense, []):
                in_cardsets = "3, " + in_cardsets
            if person in cardsets[2].get(tense, []):
                in_cardsets = "2, " + in_cardsets
            if person in cardsets[1].get(tense, []):
                in_cardsets = "1, " + in_cardsets
            if person in cardsets[0].get(tense, []):
                in_cardsets = "0, " + in_cardsets

            table.add_row(person, get_for_tense_person(tense, person, vc), in_cardsets)

        console = Console()
        console.print(table)
    
    print(f"Gerundio: {gr}")
    print()
    print(f"0) {infinitive}: {df}")
    print()


def iteractive():
    infinitive = click.prompt("What's the verb infinitivo?", type=str)
    infinitive = infinitive.lower()
    vc, df, gr = get_conjugations(infinitive, minimal_tenses, withDef=True, withGr=True)

    print_cardset_data(infinitive, vc, df, gr)    
    print()

    cardset_num = click.prompt("Which cardset would you like to use?", type=int)
    
    updated_def = click.prompt("Would you like to change the definition? If so, type it here", default=df, type=str)
    if updated_def:
        df = updated_def

    it_first = False
    cardlist = cardset_to_basic_card_format(infinitive, vc, df, cardsets[cardset_num], it_first)

    tags = set()
    if it_first:
        tags.add("it_front")

    for card in cardlist:
        tags.update(card["tags"])

    existing_tags = list_existing_tags(list(tags))
    if infinitive in existing_tags:
        continue_anyway = click.confirm(f"Tag {infinitive} already exist. Continue anyway?")
        if not continue_anyway:
            print("Exiting")
            return 
    
    ids = add_notes(cardlist)
    print(ids)


if __name__ == "__main__":
    iteractive()
    