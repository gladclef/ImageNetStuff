class PrefixParser:
    file = None
    prefixes = set()

    def __init__(self, file):
        self.file = file

    def parse(self):
        self.prefixes = set()
        with open(self.file, encoding="utf8") as f:
            for line in f:
                line = line.strip()
                if (len(line) > 0):
                    self.prefixes.add(line)
        return self.prefixes

    def matches_prefix(self, value):
        value = value.strip()
        return value in self.prefixes

    def count(self):
        return len(self.prefixes)

if __name__ == "__main__":
    parser = PrefixParser("people.txt")
    parser.parse()
    print(f"number of found prefixes: {parser.count()}")