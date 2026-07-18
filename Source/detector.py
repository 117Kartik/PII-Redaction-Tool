import re
import spacy


class Detector:

    def __init__(self):

        self.nlp = spacy.load("en_core_web_lg")

        self.patterns = {

            "EMAIL": re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
            ),

            "PHONE": re.compile(
                r"(?:\+91[-\s]?)?[6-9]\d{9}\b"
            ),

            "DOB": re.compile(
                r"\b(?:\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2})\b"
            ),

            "IP_ADDRESS": re.compile(
                r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
            ),

            "CREDIT_CARD": re.compile(
                r"\b(?:\d{4}[- ]?){3}\d{4}\b"
            ),

            "PAN": re.compile(
                r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
            ),

            "AADHAAR": re.compile(
                r"\b\d{4}\s?\d{4}\s?\d{4}\b"
            ),

            "PASSPORT": re.compile(
                r"\b[A-Z][0-9]{7}\b"
            )
        }

        self.rule_pattern = re.compile(
            r"\b[A-Z]{2,}(?:\s+[A-Z]{2,}){1,5}\b"
        )

        self.blacklist = {
            "RED",
            "HERRING",
            "PROSPECTUS",
            "LIMITED",
            "CORPORATE",
            "IDENTITY",
            "NUMBER",
            "EMAIL",
            "TELEPHONE",
            "OUR",
            "PROMOTERS",
            "FAMILY",
            "TRUST",
            "INDIA",
            "MAHARASHTRA",
            "FRESH",
            "ISSUE",
            "SALE",
            "COMPANY",
            "SECRETARY",
            "OFFICER"
        }

        self.spacy_blacklist = {
            "Email",
            "Cap Price",
            "Floor Price",
            "first",
            "million",
            "Book Running Lead Managers",
            "Book Building Process",
            "Basis for the Offer Price",
            "The Floor Price"
        }

    def detect_regex(self, text):

        matches = []

        for pii_type, pattern in self.patterns.items():

            for match in pattern.finditer(text):

                matches.append({
                    "type": pii_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "source": "regex"
                })

        return matches

    def detect_rules(self, text):

        matches = []

        for match in self.rule_pattern.finditer(text):

            value = match.group().strip()

            words = value.split()

            if len(words) < 2:
                continue

            if any(word in self.blacklist for word in words):
                continue

            matches.append({
                "type": "PERSON",
                "value": value,
                "start": match.start(),
                "end": match.end(),
                "source": "rule"
            })

        return matches

    def detect_promoter_names(self, text):

        matches = []

        pattern = re.compile(
            r"\b[A-Z]{2,}(?:\s+[A-Z]{2,}){2,4}\b"
        )

        for match in pattern.finditer(text):

            value = match.group().strip()

            if "FAMILY TRUST" in value:
                continue

            if "LIMITED" in value:
                continue

            if "CORPORATE" in value:
                continue

            if "IDENTITY" in value:
                continue

            matches.append({
                "type": "PERSON",
                "value": value,
                "start": match.start(),
                "end": match.end(),
                "source": "promoter_rule"
            })

        return matches

    def clean_spacy_entity(self, value, label):

        value = value.strip()

        suffixes = [
            " Company",
            " Limited",
            " Ltd.",
            " LLP",
            " Private Limited"
        ]

        if label == "ORG":

            for suffix in suffixes:

                if value.endswith(suffix):

                    candidate = value[:-len(suffix)].strip()

                    if len(candidate.split()) >= 2:
                        return candidate, "PERSON"

        return value, label

    def detect_spacy(self, text):

        matches = []

        doc = self.nlp(text)

        allowed_entities = {
            "PERSON",
            "ORG",
            "GPE",
            "LOC"
        }

        for ent in doc.ents:

            print(f"[spaCy] {ent.text} ---> {ent.label_}")

            if ent.label_ not in allowed_entities:
                continue

            value, entity_type = self.clean_spacy_entity(
                ent.text,
                ent.label_
            )

            if value in self.spacy_blacklist:
                continue

            if len(value) <= 2:
                continue

            matches.append({
                "type": entity_type,
                "value": value,
                "start": ent.start_char,
                "end": ent.end_char,
                "source": "spacy"
            })

        return matches

    def post_process(self, matches):

        processed = []

        person_keywords = {
            "Hegde",
            "Malvadkar",
            "Shetty",
            "Kumar",
            "Singh",
            "Sharma",
            "Verma",
            "Patel",
            "Gupta"
        }

        for match in matches:

            value = match["value"]
            entity_type = match["type"]

            if entity_type == "ORG":

                words = value.split()

                if any(word in person_keywords for word in words):

                    entity_type = "PERSON"

            processed.append({
                "type": entity_type,
                "value": value,
                "start": match["start"],
                "end": match["end"],
                "source": match["source"]
            })

        return processed

    def remove_duplicates(self, matches):

        matches.sort(key=lambda x: (x["start"], -(x["end"] - x["start"])))

        filtered = []

        occupied = set()

        for match in matches:

            overlap = False

            for i in range(match["start"], match["end"]):

                if i in occupied:
                    overlap = True
                    break

            if overlap:
                continue

            filtered.append(match)

            for i in range(match["start"], match["end"]):
                occupied.add(i)

        return filtered

    def detect(self, text):

        matches = []

        matches.extend(self.detect_regex(text))
        matches.extend(self.detect_rules(text))
        matches.extend(self.detect_promoter_names(text))
        matches.extend(self.detect_spacy(text))

        matches = self.post_process(matches)

        matches = self.remove_duplicates(matches)

        matches.sort(key=lambda x: x["start"])

        return matches