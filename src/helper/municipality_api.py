from fastapi import FastAPI, HTTPException
import xml.etree.ElementTree as ET
import os

NAMESPACE = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "ex": "http://example.org/ontology#",
}

app = FastAPI(title="Municipality Class API")


def load_entries(path: str) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()
    data = {}
    for entry in root.findall(".//ex:hasEntry/rdf:Description", NAMESPACE):
        name_elem = entry.find("ex:municipalityName", NAMESPACE)
        class_elem = entry.find("ex:municipalityClass", NAMESPACE)
        if name_elem is not None and class_elem is not None:
            data[name_elem.text] = class_elem.text
    return data


ONTOLOGY_FILE = os.environ.get("MUNICIPALITY_OWL", "model_municipality_class_mapping.owl")
ENTRIES = load_entries(ONTOLOGY_FILE)


@app.get("/municipality-class/{name}")
def read_municipality_class(name: str):
    clazz = ENTRIES.get(name)
    if clazz is None:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return {"municipality": name, "municipalityClass": clazz}