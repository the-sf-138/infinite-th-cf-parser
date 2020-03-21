import argparse

parser = argparse.ArgumentParser(prog="CodeForcesParses")
parser.add_argument("--contest-number", required=False, type=int)
parser.add_argument("--problem", required=False)

import os
import subprocess
import glob

# Project local....
import parsers
import log
import runner


def create_contest_files(contest):
    main           = parsers.CodeForcesMainPageParser()
    problems       = main.get_problems(contest)
    log.info(f"found problems {', '.join(problems)}")

    problem_parser = parsers.CodeForcerProblemPageParser() 
    specs          = [ (p, problem_parser.get_test_cases(contest, p)) for p in problems ]

    os.makedirs(f"{contest}", exist_ok=True)
    os.makedirs(f"{contest}/inputs/", exist_ok=True)
    os.makedirs(f"{contest}/outputs/", exist_ok=True)

    for p, s in specs:
        log.info(f"{p} has {len(s)} test cases")
        for n, (i, o) in enumerate(s):
            with open(f"{contest}/inputs/{p.lower()}.input.{n}", "w") as fi:
                fi.write(i)
            with open(f"{contest}/outputs/{p.lower()}.output.{n}", "w") as fi:
                fi.write(o)


# TODO refactor this shit
def run_problem(problem):
    fname   = runner.get_filename(problem)
    ftype   = runner.get_filetype(fname)
    exe     = runner.get_executable(ftype, problem, fname)
    samples = runner.get_samples(problem)
    for n, (i, o) in enumerate(samples):
        cmd = f"diff <({exe} < {i}) {o}"
        print(cmd)
        r = subprocess.run(f"bash -c '{cmd}'",  shell=True)
        if r.returncode == 0:
            log.success(f"{problem}.{n} success")
        else:
            log.error(f"{problem}.{n} failed")
if __name__ == "__main__":
    args = parser.parse_args()
    if args.problem:
        run_problem(args.problem)
    elif args.contest_number:
        create_contest_files(args.contest_number)

 
