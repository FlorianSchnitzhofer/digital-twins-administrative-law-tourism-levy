#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a full OWL/RDF file for OÖ Beitragsgruppenordnung – Annex 1
"""

import json, re, requests, textwrap
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

BASE_IRI = "http://tourismlevy.lawdigitaltwin.com/dtal_tourismlevy/ooe_contribution_ontology#"
URL      = "https://ris.bka.gv.at/eli/lgbl/OB/1992/54/ANL1/LOO12004969"

translator = GoogleTranslator(source="de", target="en")

def fetch_rows() -> list[tuple[str,str,list[int]]]:
    """Return list of (code, german_text, six_ints)."""
    html = requests.get(URL, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    # grab the plain-text view hidden inside <pre> (RIS uses <pre> in printable view)
    pre = soup.find("pre")
    raw = pre.get_text("\n") if pre else soup.get_text("\n")

    pattern = re.compile(r"""
        ^\s*              # start of line
        (\d[\d./]*)       # code (digits, dot, slash allowed)
        \s+([^-.\d][^\.]+) # german label (until first ... or digits)
        \.+\s+            # dot leader
        (\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d)\s+(\d) # six ints
    """, re.VERBOSE | re.MULTILINE)

    rows = []
    for m in pattern.finditer(raw):
        code, de, *nums = m.groups()
        nums = list(map(int, nums))
        de = " ".join(de.split())  # compact
        rows.append((code, de, nums))
    return rows


def mk_individual(code, de, nums):
    en = translator.translate(de) or de  # fall back to german
    array_json = json.dumps(nums, ensure_ascii=False)
    # escape & < > for XML attributes
    def esc(txt): return (txt.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;"))
    template = f"""
    <owl:NamedIndividual rdf:about="ex:{esc(code)}">
        <rdf:type rdf:resource="ex:BusinessActivity"/>
        <activityCode rdf:datatype="xsd:string">{esc(code)}</activityCode>
        <contributionArray rdf:datatype="xsd:string">{array_json}</contributionArray>
        <rdfs:label xml:lang="de">{esc(de)}</rdfs:label>
        <rdfs:label xml:lang="en">{esc(en)}</rdfs:label>
    </owl:NamedIndividual>
    """
    return textwrap.dedent(template)


def main():
    print("Downloading Annex 1 …")
    rows = fetch_rows()
    print(f"Found {len(rows)} activity rows")

    # read the constant header from section 2 above (save it as HEADER)
    HEADER_FILE = "ontology_header.xml"
    with open(HEADER_FILE, encoding="utf-8") as fh:
        header = fh.read().rstrip()

    with open("ooe_contribution_ontology.owl", "w", encoding="utf-8") as out:
        out.write(header)
        out.write("\n    <!-- BusinessActivity individuals -->\n")
        for code, de, nums in rows:
            out.write(mk_individual(code, de, nums))
        out.write("\n</rdf:RDF>\n")

    print("✔ Written → ooe_contribution_ontology.owl")


if __name__ == "__main__":
    main()
