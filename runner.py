import os
import subprocess
import glob

import log

# Language specs
# only python3 cuz fuck py2
class Cpp: pass
class Python: pass
class Haskell: pass

FILE_TYPES = {
    Cpp     : [ ".C", ".cc", ".cpp" ],
    Python  : [ ".py" ],
    Haskell : [ ".hs" ],
    }

TO_FILE_TYPE     = { f : t for t, fs in FILE_TYPES.items() for f in fs }
VALID_FILE_TYPES = set([f.split(".")[-1] for t, fs in FILE_TYPES.items() for f in fs ])

def get_executable(type, problem, fname):
    if type == Cpp:
        cmd = f"g++ -std=c++14 {fname} -o {problem}"
        try:
            subprocess.run(cmd.split(), check=True)
            return f"./{problem}"
        except subprocess.CalledProcessError as e:
            log.error(str(e))
            return None
    elif type == Haskell:
        return f"runhaskell {fname}"
    elif type == Python:
        return f"python3 {fname}"
    else:
        log.error("Invalid type {type} {problem} {fname}")

def get_filename(problem, hint=None):
    files       = os.listdir()
    valid_types = VALID_FILE_TYPES if (hint is None) else set([ f.split(".")[-1] for f in FILE_TYPES[hint]])
    candidates  = [ f for f in files if f.lower().startswith(problem.lower() + ".")
                    and not f.endswith("~")
                    and (f.lower().split(".")[-1] in valid_types)]
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
