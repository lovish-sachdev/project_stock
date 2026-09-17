import subprocess
import sys
from pathlib import Path


def main() -> None:
    app_path = Path(__file__).parent / "streamlit_app.py"
    if not app_path.exists():
        raise FileNotFoundError(f"Streamlit app not found: {app_path}")

    subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True
    )


if __name__ == '__main__':
    main()
