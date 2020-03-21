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
info    = log_color(ENDC, "INFO")
