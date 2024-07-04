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
        cmd = f"g++ -std=c++17 {fname} -o {problem}"
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

def get_filename(problem, contest=None, hint=None):
    files       = os.listdir()
    valid_types = VALID_FILE_TYPES if (hint is None) else set([ f.split(".")[-1] for f in FILE_TYPES[hint]])
    if contest is None:
        start = f"{problem.lower()}."
    else:
        start = f"{contest}.{problem.lower()}."
    candidates  = [ f for f in files if f.lower().startswith(start)
                    and not f.endswith("~")
                    and (f.split(".")[-1] in valid_types)]
    assert len(candidates) == 1, f"[{', '.join(candidates)}]"
    return candidates[0]

def get_filetype(fname):
    ext = "." + fname.split(".")[-1]
    return TO_FILE_TYPE[ext]

def get_samples(problem, contest=None):
    problem = problem.lower()
    if contest:
        input_glob = f"inputs/{contest}.{problem}.input.*"
        output_glob = f"outputs/{contest}.{problem}.output.*"
    else:
        input_glob = f"inputs/{problem}.input.*"
        output_glob = f"outputs/{problem}.output.*"
    inputs  = [ i for i in glob.glob(input_glob) if not i.endswith("~") ]
    outputs = [ o for o in glob.glob(output_glob) if not o.endswith("~") ]
    return zip(sorted(inputs), sorted(outputs))
