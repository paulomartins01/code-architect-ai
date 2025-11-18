"""
File utility functions
"""
from pathlib import Path
from typing import List


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes"""
    return file_path.stat().st_size / (1024 * 1024)


def ensure_directory(path: Path) -> None:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)


def read_file_safe(file_path: Path) -> str:
    """Read file with fallback encoding"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def scan_code_files(
    root: Path,
    extensions: List[str],
    ignore_dirs: List[str],
    ignore_files: List[str]
) -> List[Path]:
    """Scan directory for code files"""
    files = []
    extensions_set = set(extensions)
    ignore_dirs_set = set(ignore_dirs)
    ignore_files_set = set(ignore_files)
    
    for file_path in root.rglob('*'):
        # Skip ignored directories
        if any(ignored in file_path.parts for ignored in ignore_dirs_set):
            continue
        
        # Skip ignored files
        if file_path.name in ignore_files_set:
            continue
        
        # Check extension
        if file_path.is_file() and file_path.suffix in extensions_set:
            files.append(file_path)
    
    return sorted(files)

