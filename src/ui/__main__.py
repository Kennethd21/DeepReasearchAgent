"""Allow running UI as module: python -m src.ui"""

import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "src/ui/streamlit_app.py"
    ])
