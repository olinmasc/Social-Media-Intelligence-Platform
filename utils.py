"""
utils.py - Column Detection, Data Validation, Quality Profiling, and Helper Utilities
Provides automated heuristic mapping for varied dataset schemas, data cleaning pipelines
with audit logs, and diagnostic quality reporting.
"""

import re
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np

# Synonyms dictionary for flexible column mapping
COLUMN_SYNONYMS: Dict[str, List[str]] = {
    "platform": ["platform", "social_media", "network", "channel", "source", "site", "media"],
    "post_id": ["post_id", "id", "post", "tweet_id", "uid", "item_id", "entry_id"],
    "date": ["date", "post_date", "timestamp", "created_at", "datetime", "published_at", "time", "date_time"],
    "likes": ["likes", "like_count", "num_likes", "favorites", "favs", "upvotes", "reactions"],
    "comments": ["comments", "comment_count", "num_comments", "replies", "reply_count"],
    "shares": ["shares", "share_count", "retweets", "reposts", "forwards", "retweet_count"],
    "impressions": ["impressions", "views", "reach", "view_count", "impressions_count", "total_views"],
    "text": ["text", "caption", "content", "post_text", "tweet", "message", "body", "description", "post_content"],
    "hashtags": ["hashtags", "tags", "post_tags", "hash_tags", "tag_list"],
    "sentiment": ["sentiment", "polarity", "sentiment_label", "sentiment_score", "predicted_sentiment"]
}


def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Automatically detects and maps standard fields from uploaded DataFrame columns.
    Uses normalized case and substring matching.
    """
    mapping: Dict[str, Optional[str]] = {standard: None for standard in COLUMN_SYNONYMS}
    available_cols = list(df.columns)
    
    # Clean column names for comparison
    cleaned_col_map = {col: re.sub(r"[^a-zA-Z0-9]", "", col.lower()) for col in available_cols}
    
    for standard, synonyms in COLUMN_SYNONYMS.items():
        # Exact clean match first
        for col, clean_col in cleaned_col_map.items():
            for syn in synonyms:
                clean_syn = re.sub(r"[^a-zA-Z0-9]", "", syn.lower())
                if clean_col == clean_syn:
                    mapping[standard] = col
                    break
            if mapping[standard]:
                break
                
        # Substring search if not found
        if mapping[standard] is None:
            for col, clean_col in cleaned_col_map.items():
                for syn in synonyms:
                    clean_syn = re.sub(r"[^a-zA-Z0-9]", "", syn.lower())
                    if len(clean_syn) > 2 and clean_syn in clean_col:
                        # Avoid false positives (e.g. 'id' matching 'confidence')
                        if clean_syn == "id" and clean_col != "id" and not clean_col.endswith("id"):
                            continue
                        mapping[standard] = col
                        break
                if mapping[standard]:
                    break
                    
    return mapping


def analyze_data_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Classifies DataFrame columns into numerical, categorical, date, and text types."""
    summary = {
        "numerical": [],
        "categorical": [],
        "datetime": [],
        "text": []
    }
    
    for col in df.columns:
        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            summary["datetime"].append(col)
            continue
            
        # Check numeric
        if pd.api.types.is_numeric_dtype(df[col]):
            summary["numerical"].append(col)
            continue
            
        # Try datetime conversion sample
        sample_non_null = df[col].dropna().head(20).astype(str)
        if len(sample_non_null) > 0:
            try:
                converted = pd.to_datetime(sample_non_null, format="mixed", errors="coerce")
                if converted.notnull().mean() > 0.8:
                    summary["datetime"].append(col)
                    continue
            except Exception:
                pass
                
        # String or object analysis
        avg_len = sample_non_null.apply(len).mean() if len(sample_non_null) > 0 else 0
        unique_ratio = df[col].nunique() / max(1, len(df))
        
        if avg_len > 35 or unique_ratio > 0.6:
            summary["text"].append(col)
        else:
            summary["categorical"].append(col)
            
    return summary


def assess_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Generates a comprehensive data quality diagnostic report."""
    total_rows = len(df)
    total_cols = len(df.columns)
    
    # Missing values
    missing_series = df.isnull().sum()
    missing_pct = (missing_series / total_rows * 100).round(2)
    missing_report = {
        col: {"count": int(missing_series[col]), "pct": float(missing_pct[col])}
        for col in df.columns if missing_series[col] > 0
    }
    
    # Duplicate rows
    duplicate_count = int(df.duplicated().sum())
    duplicate_pct = round((duplicate_count / total_rows * 100), 2) if total_rows > 0 else 0.0
    
    # Column types
    col_types = analyze_data_types(df)
    
    # Overall health score (0 - 100)
    penalty_missing = min(40, (df.isnull().sum().sum() / max(1, total_rows * total_cols)) * 100)
    penalty_dups = min(30, (duplicate_count / max(1, total_rows)) * 100)
    health_score = max(0, round(100 - penalty_missing - penalty_dups, 1))
    
    return {
        "total_rows": total_rows,
        "total_cols": total_cols,
        "total_cells": total_rows * total_cols,
        "duplicate_rows": duplicate_count,
        "duplicate_pct": duplicate_pct,
        "columns_with_missing": len(missing_report),
        "missing_details": missing_report,
        "column_types": col_types,
        "health_score": health_score
    }


def clean_dataset(
    df: pd.DataFrame,
    column_mapping: Dict[str, Optional[str]],
    drop_duplicates_flag: bool = True,
    missing_strategy: str = "impute_sensible" # 'impute_sensible', 'drop_rows', 'keep_as_is'
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans dataset based on user preferences and records an explicit audit log.
    Never silently modifies data without logging.
    """
    clean_df = df.copy()
    audit_log = []
    initial_rows = len(clean_df)
    
    # 1. Duplicate Handling
    if drop_duplicates_flag:
        dup_count = int(clean_df.duplicated().sum())
        if dup_count > 0:
            clean_df = clean_df.drop_duplicates().reset_index(drop=True)
            audit_log.append(f"Removed {dup_count} exact duplicate rows ({round(dup_count/initial_rows*100, 2)}% of dataset).")
        else:
            audit_log.append("No exact duplicate rows found.")
    else:
        audit_log.append("User opted to retain duplicate rows.")
        
    # 2. Date column parsing & normalization
    date_col = column_mapping.get("date")
    if date_col and date_col in clean_df.columns:
        original_nulls = clean_df[date_col].isnull().sum()
        clean_df[date_col] = pd.to_datetime(clean_df[date_col], format="mixed", errors="coerce")
        new_nulls = clean_df[date_col].isnull().sum()
        invalid_dates = int(new_nulls - original_nulls)
        if invalid_dates > 0:
            audit_log.append(f"Converted column '{date_col}' to datetime; {invalid_dates} unparseable entries set to NaT.")
        else:
            audit_log.append(f"Successfully converted column '{date_col}' to standardized datetime.")
            
    # 3. Numeric metrics coercion
    numeric_keys = ["likes", "comments", "shares", "impressions"]
    for key in numeric_keys:
        col = column_mapping.get(key)
        if col and col in clean_df.columns:
            non_num_count = pd.to_numeric(clean_df[col], errors="coerce").isnull().sum() - clean_df[col].isnull().sum()
            clean_df[col] = pd.to_numeric(clean_df[col], errors="coerce")
            if non_num_count > 0:
                audit_log.append(f"Coerced '{col}' to numeric; {non_num_count} non-numeric values replaced with NaN.")
                
    # 4. Missing value strategy
    if missing_strategy == "drop_rows":
        before_drop = len(clean_df)
        clean_df = clean_df.dropna().reset_index(drop=True)
        dropped = before_drop - len(clean_df)
        audit_log.append(f"Dropped {dropped} rows containing any missing values across all columns.")
        
    elif missing_strategy == "impute_sensible":
        imputed_counts = {}
        for key in numeric_keys:
            col = column_mapping.get(key)
            if col and col in clean_df.columns:
                null_count = clean_df[col].isnull().sum()
                if null_count > 0:
                    median_val = clean_df[col].median()
                    fill_val = 0 if np.isnan(median_val) else median_val
                    clean_df[col] = clean_df[col].fillna(fill_val)
                    imputed_counts[col] = (null_count, fill_val)
                    
        # Categorical imputations
        cat_keys = ["platform"]
        for key in cat_keys:
            col = column_mapping.get(key)
            if col and col in clean_df.columns:
                null_count = clean_df[col].isnull().sum()
                if null_count > 0:
                    clean_df[col] = clean_df[col].fillna("Unknown")
                    imputed_counts[col] = (null_count, "Unknown")
                    
        # Text imputations
        text_keys = ["text", "hashtags"]
        for key in text_keys:
            col = column_mapping.get(key)
            if col and col in clean_df.columns:
                null_count = clean_df[col].isnull().sum()
                if null_count > 0:
                    clean_df[col] = clean_df[col].fillna("")
                    imputed_counts[col] = (null_count, "empty string")
                    
        if imputed_counts:
            for c, (cnt, val) in imputed_counts.items():
                audit_log.append(f"Imputed {cnt} missing values in '{c}' using value: '{val}'.")
        else:
            audit_log.append("No missing values required imputation in core mapped fields.")
    else:
        audit_log.append("Missing values preserved as-is per configuration.")
        
    final_rows = len(clean_df)
    cleaning_summary = {
        "initial_rows": initial_rows,
        "final_rows": final_rows,
        "initial_cols": len(df.columns),
        "final_cols": len(clean_df.columns),
        "rows_removed": initial_rows - final_rows,
        "audit_log": audit_log,
        "strategy_applied": missing_strategy
    }
    
    return clean_df, cleaning_summary


def format_number(val: Optional[float], precision: int = 1) -> str:
    """Formats large numbers into compact human-readable strings (e.g., 1.5M, 24.2K)."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        val = float(val)
    except (ValueError, TypeError):
        return str(val)
        
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.{precision}f}B"
    elif abs_val >= 1_000_000:
        return f"{val / 1_000_000:.{precision}f}M"
    elif abs_val >= 1_000:
        return f"{val / 1_000:.{precision}f}K"
    elif abs_val == int(abs_val):
        return f"{int(val):,}"
    else:
        return f"{val:.{precision}f}"


def get_feature_availability(mapping: Dict[str, Optional[str]]) -> Dict[str, Tuple[bool, str]]:
    """Checks which analytics features can run based on mapped columns."""
    has_platform = mapping.get("platform") is not None
    has_date = mapping.get("date") is not None
    has_text = mapping.get("text") is not None
    has_hashtags = mapping.get("hashtags") is not None or has_text
    has_likes = mapping.get("likes") is not None
    has_impressions = mapping.get("impressions") is not None
    
    numeric_count = sum(1 for k in ["likes", "comments", "shares", "impressions"] if mapping.get(k))
    
    features = {
        "Descriptive Statistics": (True, "Requires any tabular data (Available)"),
        "Platform-wise Comparison": (has_platform and numeric_count > 0, "Requires Platform and at least one metric"),
        "Time-series Trend Analysis": (has_date and numeric_count > 0, "Requires Date and at least one metric"),
        "Engagement Rate Calculation": (numeric_count > 0 and has_impressions, "Requires Likes/Comments/Shares and Impressions denominator"),
        "Correlation Heatmap": (numeric_count >= 2, "Requires at least 2 numeric metrics"),
        "Text Word Frequency & Sentiment": (has_text, "Requires Text/Caption column"),
        "Hashtag Analytics": (has_hashtags, "Requires Hashtags or Text column"),
        "K-Means Machine Learning Clustering": (numeric_count >= 2, "Requires at least 2 numerical engagement features")
    }
    return features
