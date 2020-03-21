import argparse

parser = argparse.ArgumentParser(prog="CodeForcesParses")
parser.add_argument("--contest-number", required=False, type=int)
parser.add_argument("--problem", required=False)

import os
import subprocess
import glob

# Shit log utilities
GREEN  = '\033[32m'
RED    = '\033[31m'
YELLOW = '\033[33m'
BLUE   = '\033[34m'
ENDC   = '\033[0m'

def log_color(color=ENDC, type="INFO"):
    def f(s):
        print(color + f"==== [{type}] : {s}" + ENDC)
    return f

error   = log_color(RED, "ERROR")
success = log_color(GREEN, "OK")

# Language specs
# only python3 cuz fuck py2
class Cpp: pass
class Python: pass
FILE_TYPES = {
    Cpp    : [ ".C", ".cc", ".cpp" ],
    Python : [ ".py" ]
    }

TO_FILE_TYPE = { f : t for t, fs in FILE_TYPES.items() for f in fs }

import requests
from html.parser import HTMLParser

class CodeForcerProblemPageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.awaiting = False
        self.div_stack = []
        self.temp = None
        self.inputs = []
        self.outputs = []

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
        assert self.temp is None
        if self.awaiting:
            self.temp = data

    def handle_endtag(self, tag):
        # will fuck up on a nested table
        # shoud do a stack obv
        if self.div_stack and tag == "div":
            data_type = self.div_stack.pop()
            if data_type == "input":
                self.inputs.append(self.temp)
                self.temp = None
            elif data_type == "output":
                self.outputs.append(self.temp)
                self.temp = None
        if tag == "pre":
            self.awaiting = False

    def get_test_cases(self, contest, problem):
        url = f"https://codeforces.com/contest/{contest}/problem/{problem.upper()}"
        r = requests.get(url)
        self.feed(r.text)
        result = list(zip(self.inputs, self.outputs))
        self.inputs = []
        self.outputs = []
        return result

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
        r = requests.get(url)
        self.feed(r.text)
        self.contest = None
        return sorted(list(self.problems))

def create_contest_files(contest):
    main = CodeForcesMainPageParser()
    problems = main.get_problems(contest)
    problem_parser = CodeForcerProblemPageParser() 
    specs = [ (p, problem_parser.get_test_cases(contest, p)) for p in problems ]

    os.makedirs(f"{contest}", exist_ok=True)
    os.makedirs(f"{contest}/inputs/", exist_ok=True)
    os.makedirs(f"{contest}/outputs/", exist_ok=True)
    success(f"found problems {', '.join(problems)}")

    for p, s in specs:
        success(f"{p} has {len(s)} test cases")
        for n, (i, o) in enumerate(s):
            with open(f"{contest}/inputs/{p.lower()}.input.{n}", "w") as fi:
                fi.write(i)
            with open(f"{contest}/outputs/{p.lower()}.output.{n}", "w") as fi:
                fi.write(o)

def get_executable(type, problem, fname):
    if type == Cpp:
        cmd = f"g++ -std=c++14 {fname} -o {problem}"
        try:
            subproccess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return f"./{problem}"
        except subproccess.CalledProcessError:
            return None
    elif type == Python:
            return f"python3 {fname}"

def get_filename(problem):
    files = os.listdir()
    candidates = [ f for f in files if f.lower().startswith(problem.lower() + ".") and not f.endswith("~")]
    assert len(candidates) == 1, ", ".join(candidates)
    return candidates[0]

def get_filetype(fname):
    ext = "." + fname.split(".")[-1]
    return TO_FILE_TYPE[ext]

def get_samples(problem):
    problem = problem.lower()
    inputs = glob.glob(f"inputs/{problem}.input.*")
    outputs = glob.glob(f"outputs/{problem}.output.*")
    return zip(sorted(inputs), sorted(outputs))

def run_problem(problem):
    fname = get_filename(problem)
    ftype = get_filetype(fname)
    exe   = get_executable(ftype, problem, fname)
    samples = get_samples(problem)
    for i, o in samples:
        cmd = f"diff <({exe} < {i}) {o}"
        print(cmd)
        subprocess.run(f"bash -c '{cmd}'",  shell=True)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.problem:
        run_problem(args.problem)
    elif args.contest_number:
        create_contest_files(args.contest_number)

 
