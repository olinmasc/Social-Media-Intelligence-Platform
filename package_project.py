"""
package_project.py - Bundles the mini-project into a clean distribution ZIP archive.
Excludes venv, cache, and temporary files.
"""

import os
import zipfile

def create_project_zip(zip_filename: str = "social_media_analytics_bda_project.zip"):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(project_dir, zip_filename)
    
    exclude_dirs = {"venv", ".git", "__pycache__", ".pytest_cache", ".gemini", ".idea"}
    exclude_exts = {".pyc", ".pyo", ".zip"}
    exclude_files = {".DS_Store"}
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files or any(file.endswith(ext) for ext in exclude_exts):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)
                zipf.write(full_path, rel_path)
                
    file_size_mb = round(os.path.getsize(zip_path) / (1024 * 1024), 2)
    print(f"Created ZIP package: {zip_path} ({file_size_mb} MB)")
    return zip_path

if __name__ == "__main__":
    create_project_zip()
