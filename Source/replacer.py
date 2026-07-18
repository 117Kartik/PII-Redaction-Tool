import random
import string

from faker import Faker


class Replacer:

    def __init__(self):

        self.fake = Faker()

        self.mapping = {}

        self.generators = {
            "EMAIL": self.fake.email,
            "PHONE": self.generate_phone,
            "DOB": self.generate_dob,
            "IP_ADDRESS": self.fake.ipv4,
            "CREDIT_CARD": self.fake.credit_card_number,
            "PAN": self.generate_pan,
            "AADHAAR": self.generate_aadhaar,
            "PASSPORT": self.generate_passport,
            "PERSON": self.fake.name,
            "ORG": self.generate_company,
            "GPE": self.generate_location,
            "LOC": self.generate_location,
        }

    def generate_phone(self):

        return "".join(random.choices("6789", k=1)) + "".join(
            random.choices(string.digits, k=9)
        )

    def generate_dob(self):

        return self.fake.date(pattern="%d/%m/%Y")

    def generate_pan(self):

        return (
            "".join(random.choices(string.ascii_uppercase, k=5))
            + "".join(random.choices(string.digits, k=4))
            + random.choice(string.ascii_uppercase)
        )

    def generate_aadhaar(self):

        return "".join(random.choices(string.digits, k=12))

    def generate_passport(self):

        return (
            random.choice(string.ascii_uppercase)
            + "".join(random.choices(string.digits, k=7))
        )

    def generate_company(self):

        suffixes = [
            "Ltd.",
            "Limited",
            "Private Limited",
            "Industries",
            "Technologies"
        ]

        return (
            self.fake.company().split(",")[0]
            + " "
            + random.choice(suffixes)
        )

    def generate_location(self):

        return f"{self.fake.city()}, India"

    def replace(self, match):

        original = match["value"]

        if original in self.mapping:
            return self.mapping[original]

        generator = self.generators.get(match["type"])

        if generator:
            replacement = generator()
        else:
            replacement = original

        self.mapping[original] = replacement

        return replacement

    def build_run_map(self, paragraph):

        run_map = []

        position = 0

        for run_index, run in enumerate(paragraph.runs):

            for offset in range(len(run.text)):

                run_map.append({
                    "position": position,
                    "run": run_index,
                    "offset": offset
                })

                position += 1

        return run_map

    def replace_match(self, paragraph, match):

        original = match["value"]
        replacement = self.replace(match)

        full_text = "".join(run.text for run in paragraph.runs)

        start = full_text.find(original)

        if start == -1:
            return

        end = start + len(original)

        run_map = self.build_run_map(paragraph)

        if end > len(run_map):
            return

        start_info = run_map[start]
        end_info = run_map[end - 1]

        start_run = paragraph.runs[start_info["run"]]
        end_run = paragraph.runs[end_info["run"]]

        if start_info["run"] == end_info["run"]:

            text = start_run.text

            start_run.text = (
                text[:start_info["offset"]]
                + replacement
                + text[end_info["offset"] + 1:]
            )

            return

        start_run.text = (
            start_run.text[:start_info["offset"]]
            + replacement
        )

        end_run.text = (
            end_run.text[end_info["offset"] + 1:]
        )

        for i in range(
            start_info["run"] + 1,
            end_info["run"]
        ):
            paragraph.runs[i].text = ""

    def replace_in_paragraph(self, paragraph, matches):

        matches.sort(
            key=lambda x: x["start"],
            reverse=True
        )

        for match in matches:

            self.replace_match(paragraph, match)