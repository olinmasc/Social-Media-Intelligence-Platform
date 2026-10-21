"""
database.py - SQLite Database Management Module
Handles metadata storage, analysis runs, results persistence, and history tracking.
Large datasets are stored on disk; SQLite stores metadata, parameters, and analysis summaries.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "analytics_database.db")


def get_connection() -> sqlite3.Connection:
    """Creates directory if needed and returns SQLite connection with row factory."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the database schema with required tables."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Table 1: datasets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                col_count INTEGER NOT NULL,
                file_size_kb REAL NOT NULL,
                detected_columns TEXT,
                cleaning_summary TEXT,
                upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table 2: analysis_runs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER,
                analysis_type TEXT NOT NULL,
                parameters TEXT,
                status TEXT NOT NULL,
                execution_time_sec REAL,
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL
            )
        """)

        # Table 3: analysis_results
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER NOT NULL,
                dataset_id INTEGER,
                metric_name TEXT,
                summary_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES analysis_runs(id) ON DELETE CASCADE,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL
            )
        """)
        
        conn.commit()


def register_dataset(
    filename: str,
    filepath: str,
    row_count: int,
    col_count: int,
    file_size_kb: float,
    detected_columns: Optional[Dict[str, Any]] = None,
    cleaning_summary: Optional[Dict[str, Any]] = None
) -> int:
    """Inserts dataset metadata and returns the generated dataset ID."""
    init_db()
    detected_json = json.dumps(detected_columns or {})
    cleaning_json = json.dumps(cleaning_summary or {})
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO datasets (filename, filepath, row_count, col_count, file_size_kb, detected_columns, cleaning_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (filename, filepath, row_count, col_count, file_size_kb, detected_json, cleaning_json)
        )
        conn.commit()
        return cursor.lastrowid


def get_all_datasets() -> List[Dict[str, Any]]:
    """Retrieves all registered datasets ordered by newest first."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets ORDER BY upload_timestamp DESC")
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["detected_columns"] = json.loads(d["detected_columns"] or "{}")
            except Exception:
                d["detected_columns"] = {}
            try:
                d["cleaning_summary"] = json.loads(d["cleaning_summary"] or "{}")
            except Exception:
                d["cleaning_summary"] = {}
            results.append(d)
        return results


def get_dataset_by_id(dataset_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves specific dataset by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["detected_columns"] = json.loads(d["detected_columns"] or "{}")
        except Exception:
            d["detected_columns"] = {}
        try:
            d["cleaning_summary"] = json.loads(d["cleaning_summary"] or "{}")
        except Exception:
            d["cleaning_summary"] = {}
        return d


def record_analysis_run(
    dataset_id: Optional[int],
    analysis_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    execution_time_sec: float = 0.0
) -> int:
    """Records an analysis execution run and returns its run ID."""
    init_db()
    param_json = json.dumps(parameters or {})
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_runs (dataset_id, analysis_type, parameters, status, execution_time_sec)
            VALUES (?, ?, ?, ?, ?)
            """,
            (dataset_id, analysis_type, param_json, status, execution_time_sec)
        )
        conn.commit()
        return cursor.lastrowid


def save_analysis_results(
    run_id: int,
    dataset_id: Optional[int],
    summary_dict: Dict[str, Any],
    metric_name: str = "full_summary"
) -> int:
    """Stores full analysis results snapshot in JSON format."""
    init_db()
    summary_json = json.dumps(summary_dict, default=str)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_results (run_id, dataset_id, metric_name, summary_json)
            VALUES (?, ?, ?, ?)
            """,
            (run_id, dataset_id, metric_name, summary_json)
        )
        conn.commit()
        return cursor.lastrowid


def get_analysis_history(limit: int = 25) -> List[Dict[str, Any]]:
    """Retrieves recent analysis runs joined with dataset metadata."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                r.id as run_id,
                r.dataset_id,
                d.filename as dataset_filename,
                r.analysis_type,
                r.status,
                r.execution_time_sec,
                r.run_timestamp,
                r.parameters,
                res.id as result_id
            FROM analysis_runs r
            LEFT JOIN datasets d ON r.dataset_id = d.id
            LEFT JOIN analysis_results res ON r.id = res.run_id
            ORDER BY r.run_timestamp DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        history = []
        for r in rows:
            item = dict(r)
            try:
                item["parameters"] = json.loads(item["parameters"] or "{}")
            except Exception:
                item["parameters"] = {}
            history.append(item)
        return history


def get_analysis_result_by_run_id(run_id: int) -> Optional[Dict[str, Any]]:
    """Fetches stored summary JSON for a specific run ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT res.*, r.analysis_type, r.run_timestamp, d.filename
            FROM analysis_results res
            JOIN analysis_runs r ON res.run_id = r.id
            LEFT JOIN datasets d ON res.dataset_id = d.id
            WHERE res.run_id = ?
            ORDER BY res.id DESC
            LIMIT 1
            """,
            (run_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        res_dict = dict(row)
        try:
            res_dict["summary_json"] = json.loads(res_dict["summary_json"])
        except Exception:
            pass
        return res_dict


def delete_run(run_id: int) -> bool:
    """Deletes an analysis run and associated results."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_results WHERE run_id = ?", (run_id,))
        cursor.execute("DELETE FROM analysis_runs WHERE id = ?", (run_id,))
        conn.commit()
        return True


def clear_all_history() -> bool:
    """Clears history while keeping dataset records."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_results")
        cursor.execute("DELETE FROM analysis_runs")
        conn.commit()
        return True
