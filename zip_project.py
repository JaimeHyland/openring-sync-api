#!/usr/bin/env python3
"""
Create a zip archive of the project files.

Run from inside the project root:

    python zip_project.py

Optional:

    python zip_project.py --out my_backend_submission.zip
"""

from __future__ import annotations

import argparse
import fnmatch
from pathlib import Path
import zipfile
from datetime import datetime


EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    "htmlcov",
    ".idea",
    ".vscode",
}

EXCLUDED_FILES = {
    ".DS_Store",
    "Thumbs.db",
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    "db.sqlite3",
    "database.sqlite",
    "database.sqlite3",
    "zip_project.py",
}

EXCLUDED_PATTERNS = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.log",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.zip",
    "*.tar",
    "*.tar.gz",
    "*.tgz",
    "*.gz",
    ".coverage",
    "coverage.xml",
}


def should_exclude(path: Path, project_root: Path) -> bool:
    relative_path = path.relative_to(project_root)

    if any(part in EXCLUDED_DIRS for part in relative_path.parts):
        return True

    if path.name in EXCLUDED_FILES:
        return True

    relative_posix = relative_path.as_posix()

    for pattern in EXCLUDED_PATTERNS:
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(relative_posix, pattern):
            return True

    return False


def create_zip(project_root: Path, output_path: Path) -> None:
    output_path = output_path.resolve()

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        for path in sorted(project_root.rglob("*")):
            if path.is_dir():
                continue

            if path.resolve() == output_path:
                continue

            if should_exclude(path, project_root):
                continue

            archive_name = path.relative_to(project_root).as_posix()
            zip_file.write(path, archive_name)

    print(f"Created zip file: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Zip the current backend project.")
    parser.add_argument(
        "--out",
        default=None,
        help="Output zip filename. Default: <project-folder-name>_submission_<timestamp>.zip",
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.out:
        output_path = Path(args.out)
    else:
        output_path = project_root.parent / f"{project_root.name}_submission_{timestamp}.zip"

    create_zip(project_root, output_path)


if __name__ == "__main__":
    main()
