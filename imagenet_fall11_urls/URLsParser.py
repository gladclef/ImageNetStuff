import csv
import sys

class URLsParser:
    file = None
    notify_interval = None
    csvfile = None
    csviter = None
    line_num = None

    def __init__(self, file, notify_interval=None):
        self.file = file
        self.notify_interval = notify_interval

    def __iter__(self):
        return self

    def __next__(self):
        if (self.csvfile == None):
            f = open(self.file, encoding="utf8", errors="replace")
            self.csvfile = csv.reader(f, delimiter='\t')
            self.csviter = iter(self.csvfile)
            self.line_num = 0
        self.line_num += 1
        if (self.notify_interval != None and self.line_num % self.notify_interval == 0):
            print(f"parsed line {self.line_num:,}")
        return next(self.csviter)

    def parse_file(self, line_limit=None, print_row_stats=False):
        self.line_num = 0
        max_cols = 0
        min_cols = sys.maxsize
        try:
            for row in self:
                max_cols = max(len(row), max_cols)
                min_cols = min(len(row), min_cols)
                if (len(row) > 2):
                    print(row)
                self.line_num += 1
                if (line_limit != None and self.line_num >= line_limit):
                    break
        except Exception as e:
            print(f"exception on line: {self.csvfile.line_num}")
            raise e
        if (print_row_stats):
            print(f"min columns: {min_cols}, max columns: {max_cols}")

    def read_line(self, line_num, context_size=0):
        with open(self.file, encoding="utf8", errors="replace") as f:
            i = 0
            try:
                for line in f:
                    if (i >= line_num - context_size):
                        print(f"{i:<6} {line}")
                        if (i > line_num + context_size):
                            break
                    i += 1
                    if (self.notify_interval != None and i % self.notify_interval == 0):
                        print(f"parsed line {i:,}")
            except Exception as e:
                print(f"exception on line {i}")
                raise e

if __name__ == "__main__":
    parser = URLsParser("fall11_urls.txt", notify_interval=(10**6))
    #parser.parse_file(print_row_stats=True)
    parser.read_line(line_num=1294, context_size=3)