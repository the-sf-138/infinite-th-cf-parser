import os
import subprocess
import glob

# Language specs
# only python3 cuz fuck py2
class Cpp: pass
class Python: pass

FILE_TYPES = {
    Cpp    : [ ".C", ".cc", ".cpp" ],
    Python : [ ".py" ]
    }

TO_FILE_TYPE = { f : t for t, fs in FILE_TYPES.items() for f in fs }

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
