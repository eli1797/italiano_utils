import re
from collections import defaultdict

from anki_ops import search_notes, get_tags_for_note, notes_info, add_notes




def map_infinitive_to_note_id():
    """
    reduce to just the infinitive verb tag by filtering other tags
    return a map from infinitive verb to note id
    """   
    tags_filter = {'italiano_utils', 'passato_prossimo', 'presente', 'leech', 'infinito', 'imperfetto', 'futuro', 'itutils:v0.0','it_front'}

    res = search_notes("deck:italiano tag:it_front")

    inf_cards_map = defaultdict(list)
    inf_card_map = {}
    for note in res: 
        try:
            tags = get_tags_for_note(note)
            tags = set(tags)
            specific_tags = tags.difference(tags_filter)
            # print(specific_tags)

            if len(specific_tags) != 1:
                raise RuntimeError("There should be exactly one tag left")
            
            inf_form = specific_tags.pop()
            inf_cards_map[inf_form].append(note)

            if "infinito" in tags:
                inf_card_map[inf_form] = note

        except Exception as e:
            continue

    print(inf_cards_map)
    return inf_cards_map, inf_card_map


def strip_sound_tags(text):
    """
    Remove [sound:...] tags from text.
    """
    pattern = r'\[sound:.*?\]'
    return re.sub(pattern, '', text)


def main():
    inf_cards, inf_card = map_infinitive_to_note_id()


    for _, card in inf_card.items():
        info = notes_info([card])
        c = info[0]
       
        del c["noteId"]
        del c["cards"]
        del c["mod"]
        c["tags"].remove("it_front")

        c["fields"]["Front"] = strip_sound_tags(c["fields"]["Front"]["value"])
        c["fields"]["Back"] = strip_sound_tags(c["fields"]["Back"]["value"])
        
        old_front = c["fields"]["Front"]
        old_back = c["fields"]["Back"]
        c["fields"]["Front"] = old_back
        c["fields"]["Back"] = old_front

        c["tags"].append("it_eng_front_swap")

        c["deckName"] = "Italiano"
    
        print(c)

        print("----")
        add_notes([c])
        # break


if __name__ == "__main__":
    main()