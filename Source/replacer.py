from faker import Faker


class Replacer:

    def __init__(self):

        self.fake = Faker()
        self.mapping = {}

    def replace(self, match):

        original = match["value"]

        if original in self.mapping:
            return self.mapping[original]

        if match["type"] == "EMAIL":
            replacement = self.fake.email()
        else:
            replacement = original

        self.mapping[original] = replacement

        return replacement

    def replace_in_paragraph(self, paragraph, matches):

        for match in matches:

            original = match["value"]
            replacement = self.replace(match)

            for run in paragraph.runs:

                if original in run.text:
                    run.text = run.text.replace(original, replacement)