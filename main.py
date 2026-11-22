"""Copy the checked-in front page to the make.fun output directory."""
import os
import shutil
from pathlib import Path


def main():
    source = Path(__file__).resolve().with_name("entry.png")
    output = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "output")
    output.mkdir(parents=True, exist_ok=True)
    destination = output / source.name
    if not destination.exists() or not destination.samefile(source):
        shutil.copyfile(source, destination)


if __name__ == "__main__":
    main()
