import requests
from html.parser import HTMLParser

import log

# For each problem to find all the test cases
class CodeForcerProblemPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.awaiting  = False
        self.div_stack = []
        self.temp      = []
        self.inputs    = []
        self.outputs   = []

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            attrs = { k : v for k, v in attrs }
            if attrs.get("class", "") == "input":
                self.div_stack.append("input")
            elif attrs.get("class", "") == "output":
                self.div_stack.append("output")
            elif self.div_stack:
                self.div_stack.append(tag)
        elif self.div_stack and tag == "pre":
            self.awaiting = True

    def handle_data(self, data):
        if self.awaiting:
            self.temp.append(data.strip("\n").strip(" ") + "\n")

    def handle_endtag(self, tag):
        # the end tag of the stack tells us what data it is
        if self.div_stack and tag == "div":
            data_type = self.div_stack.pop()
            if data_type == "input":
                self.inputs.append("".join(self.temp))
                self.temp = []
            elif data_type == "output":
                self.outputs.append("".join(self.temp))
                self.temp = []
        if tag == "pre":
            self.awaiting = False

    def get_test_cases(self, contest, problem):
        url     = f"https://codeforces.com/contest/{contest}/problem/{problem.upper()}"
        headers = {
            'User-Agent': 'Lynx/2.8.9rel.1 libwww-FM/2.14 SSL-MM/1.4.1'
        }
        webpage = requests.get(url, headers=headers)

        try:
            self.feed(webpage.text)
            return list(zip(self.inputs, self.outputs))
        finally:
            self.inputs  = []
            self.outputs = []

# For the main contest page to find all the problems
class CodeForcesMainPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.in_table = False
        self.problems = set()

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            attrs = { k : v for k, v in attrs }
            if attrs["class"] == "problems":
                assert not self.in_table
                self.in_table = True
        elif self.in_table:
            if tag == "a":
                attrs = { k : v for k, v in attrs }
                if attrs.get("href", "").startswith(f"/contest/{self.contest}/problem"):
                    self.problems.add(attrs["href"].split("/")[-1])

    def handle_endtag(self, tag):
        # will fuck up on a nested table
        # shoud do a stack obv
        if self.in_table and tag == "table":
            self.in_table = False

    def get_problems(self, contest):
        self.contest = contest
        url = f"https://codeforces.com/contest/{self.contest}"
        headers = {
            'User-Agent': 'Lynx/2.8.9rel.1 libwww-FM/2.14 SSL-MM/1.4.1'
        }
        r = requests.get(url, headers=headers)
        open("debug.html", "w").write(r.text)
        self.feed(r.text)
        self.contest = None
        return sorted(list(self.problems))

