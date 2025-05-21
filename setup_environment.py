# setup_environment.py

import subprocess
import sys

class SetupEnvironment:
    def __init__(self):
        self.libraries = [
            "pandas",
            "openpyxl",
            "matplotlib",
            "seaborn"
        ]

    def install_libraries(self):
        for lib in self.libraries:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

    def import_libraries(self):
        global pd, np, math, plt, sns

        import pandas as pd
        import numpy as np
        import math
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Enable inline plotting
        plt.style.use('seaborn-whitegrid')
        plt.ion()
        sns.set()

    def setup(self):
        self.install_libraries()
        self.import_libraries()
