import sys
from pathlib import Path


backend_directory = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_directory))

from main import app


app = app