import requests

URL = "http://localhost:8765"

### Decks 

def list_decks() -> list[str]:
    payload = {"action": "deckNames", "version": 6}
    result = _make_request(payload)
    
    out = []
    for name in result.get("result", []):
        out.append(name)
    return out


### Models

def list_models() -> list[str]:
    payload = {"action": "modelNames", "version": 6}
    result = _make_request(payload)
    
    out = []
    for name in result.get("result", []):
        out.append(name)
    return out


def get_model_fields(model_name: str) -> list[str]:
    payload = {"action": "modelFieldNames", "version": 6, "params": {"modelName": model_name}}
    result = _make_request(payload)
    
    out = []
    for name in result.get("result", []):
        out.append(name)
    return out


def validate_model(model_name: str):
    models = list_models()
    if not model_name in models:
        return Exception(f"Model {model_name} not found")
    

## Notes
    
def add_notes(notes: list[dict]) -> list[int]:
    """
    add notes after doing some validation
    returns list of note ids
    """
    valid_models = list_models()
    for note in notes:
        model_name = note.get("modelName", False)
        if not model_name or model_name not in valid_models:
            raise ValueError(f"Note model name {model_name} does not match {model_name}")
    
    if not can_add_notes(notes):
        # TODO: improve this by returning a list of which notes failed
        raise ValueError("Cannot add notes")
    
    payload = {"action": "addNotes", "version": 6, "params": {"notes": notes}}
    result = _make_request(payload)
    return result.get("result", [])


def can_add_notes(notes: list[dict]) -> bool:
    payload = {"action": "canAddNotes", "version": 6, "params": {"notes": notes}}
    result = _make_request(payload)
    bools = result.get("result", []) 
    return all(bools)


def search_notes(query: str) -> bool:
    payload = {"action": "findCards", "version": 6, "params": {"query": query}}
    result = _make_request(payload)
    result = result.get("result", []) 
    return result


def notes_info(note_ids: list[int]) -> list[dict]:
    payload = {"action": "notesInfo", "version": 6,"params": {"notes": note_ids}}
    result = _make_request(payload)
    result = result.get("result", []) 
    return result

## Tags

def does_tag_exist(tag: str) -> bool:
    tags = list_tags()
    return tag in tags


def list_tags() -> list[str]:
    payload = {"action": "getTags", "version": 6}
    result = _make_request(payload)

    out = []
    for name in result.get("result", []):
        out.append(name)
    return out


def get_tags_for_note(note_id: int) -> list[str]:
    payload = {"action": "getNoteTags", "version": 6, "params": {"note": note_id}}
    result = _make_request(payload)
    return result.get("result", []) 


def list_existing_tags(new_tags: list[str]) -> list[str]:
    all_tags = list_tags()
    return [tag for tag in new_tags if tag in all_tags]

## Helpers

def _make_request(payload: dict) -> dict:
    response = requests.post(URL, json=payload)
    result = response.json()
    if result.get("error"):
        raise Exception(result["error"])
    return result



if __name__ == "__main__":
    decks = list_decks()    
    print(decks)

    models = list_models()
    print(models)

    fields = get_model_fields("Basic")
    print(fields)