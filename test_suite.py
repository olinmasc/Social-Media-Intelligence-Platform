"""
test_suite.py - Automated Comprehensive Test Suite
Validates application reliability against all specified edge cases:
1. Standard generated sample dataset.
2. Dataset with different column names (synonyms).
3. Dataset containing missing values and duplicates.
4. Dataset with text but no engagement metrics.
5. Dataset with engagement metrics but no text.
6. Empty or invalid dataset.
"""

import os
import io
import pandas as pd
import numpy as np

from utils import detect_columns, assess_data_quality, clean_dataset, get_feature_availability
from analytics import AnalyticsEngine
from database import (
    init_db,
    register_dataset,
    record_analysis_run,
    save_analysis_results,
    get_analysis_history,
    get_dataset_by_id
)

def run_tests():
    print("=" * 60)
    print("STARTING COMPREHENSIVE AUTOMATED TEST SUITE")
    print("=" * 60)
    init_db()
    
    # ---------------------------------------------------------
    # TEST 1: Standard Sample Dataset
    # ---------------------------------------------------------
    print("\n[TEST 1] Testing standard generated sample dataset...")
    sample_path = "data/sample_social_media.csv"
    assert os.path.exists(sample_path), "Sample dataset missing!"
    df1 = pd.read_csv(sample_path)
    assert len(df1) >= 500, f"Sample dataset should have >= 500 rows, found {len(df1)}"
    
    mapping1 = detect_columns(df1)
    assert mapping1["likes"] is not None and mapping1["platform"] is not None
    quality1 = assess_data_quality(df1)
    assert quality1["health_score"] > 80
    
    clean1, summary1 = clean_dataset(df1, mapping1)
    engine1 = AnalyticsEngine(clean1, mapping1)
    res1 = engine1.run_full_pipeline(n_clusters=3)
    assert res1["engagement_metrics"]["total_posts"] == len(clean1)
    assert res1["clustering"]["available"] is True
    print("  -> PASSED: Sample dataset processed, analyzed, and clustered cleanly.")

    # ---------------------------------------------------------
    # TEST 2: CSV with Different Column Names (Synonyms)
    # ---------------------------------------------------------
    print("\n[TEST 2] Testing dataset with alternative column names...")
    alt_df = pd.DataFrame({
        "network": ["Twitter", "Instagram", "LinkedIn"],
        "entry_id": ["E101", "E102", "E103"],
        "timestamp": ["2024-05-01 10:00:00", "2024-05-02 12:00:00", "2024-05-03 14:00:00"],
        "favs": [120, 250, 410],
        "replies": [15, 30, 45],
        "reposts": [8, 12, 22],
        "reach": [3000, 6500, 9200],
        "content": ["Exciting announcement today!", "Behind the scenes photo", "Career advice thread"],
        "tags": ["#news", "#photos", "#career"]
    })
    mapping2 = detect_columns(alt_df)
    assert mapping2["platform"] == "network", f"Expected network, got {mapping2['platform']}"
    assert mapping2["likes"] == "favs", f"Expected favs, got {mapping2['likes']}"
    assert mapping2["comments"] == "replies", f"Expected replies, got {mapping2['comments']}"
    assert mapping2["shares"] == "reposts", f"Expected reposts, got {mapping2['shares']}"
    assert mapping2["impressions"] == "reach", f"Expected reach, got {mapping2['impressions']}"
    assert mapping2["text"] == "content", f"Expected content, got {mapping2['text']}"
    assert mapping2["hashtags"] == "tags", f"Expected tags, got {mapping2['hashtags']}"
    
    clean2, summary2 = clean_dataset(alt_df, mapping2)
    engine2 = AnalyticsEngine(clean2, mapping2)
    res2 = engine2.run_full_pipeline(n_clusters=2)
    assert res2["engagement_metrics"]["total_engagement"] == (120+250+410 + 15+30+45 + 8+12+22)
    print("  -> PASSED: Alternative column synonyms correctly identified and mapped.")

    # ---------------------------------------------------------
    # TEST 3: Dataset with Missing Values & Duplicates
    # ---------------------------------------------------------
    print("\n[TEST 3] Testing dataset with missing values and duplicate rows...")
    dirty_df = pd.DataFrame({
        "post_id": ["P1", "P2", "P2", "P3", "P4"], # Duplicate P2
        "platform": ["Twitter", "Instagram", "Instagram", None, "LinkedIn"],
        "likes": [50, 100, 100, np.nan, 200],
        "comments": [5, np.nan, np.nan, 10, 20],
        "text": ["Test 1", "Test 2", "Test 2", "Test 3", None]
    })
    mapping3 = detect_columns(dirty_df)
    quality3 = assess_data_quality(dirty_df)
    assert quality3["duplicate_rows"] == 1
    assert quality3["columns_with_missing"] >= 3
    
    clean3, summary3 = clean_dataset(dirty_df, mapping3, drop_duplicates_flag=True, missing_strategy="impute_sensible")
    assert len(clean3) == 4, f"Expected 4 rows after dropping duplicate, got {len(clean3)}"
    assert clean3["likes"].isnull().sum() == 0, "Likes missing values should be imputed."
    assert clean3["platform"].isnull().sum() == 0, "Platform missing values should be imputed."
    print("  -> PASSED: Duplicates removed and missing values imputed with explicit audit log.")

    # ---------------------------------------------------------
    # TEST 4: Dataset with Text but No Engagement Columns
    # ---------------------------------------------------------
    print("\n[TEST 4] Testing dataset with text but NO engagement metrics...")
    text_only_df = pd.DataFrame({
        "post_id": [f"T_{i}" for i in range(20)],
        "platform": ["Twitter"] * 10 + ["LinkedIn"] * 10,
        "text": [f"This is a great, awesome and inspiring post number {i}! #AI #BigData" for i in range(20)]
    })
    mapping4 = detect_columns(text_only_df)
    clean4, _ = clean_dataset(text_only_df, mapping4)
    engine4 = AnalyticsEngine(clean4, mapping4)
    res4 = engine4.run_full_pipeline(n_clusters=3)
    
    assert res4["text_analytics"]["available"] is True
    assert res4["clustering"]["available"] is False # Gracefully handled
    assert "requires at least 2 numerical" in res4["clustering"]["reason"].lower()
    print("  -> PASSED: Text analytics succeeded; missing numerical metrics handled gracefully without crash.")

    # ---------------------------------------------------------
    # TEST 5: Dataset with Engagement Metrics but No Text
    # ---------------------------------------------------------
    print("\n[TEST 5] Testing dataset with engagement metrics but NO text column...")
    num_only_df = pd.DataFrame({
        "post_id": [f"N_{i}" for i in range(30)],
        "platform": ["YouTube"] * 15 + ["Instagram"] * 15,
        "likes": np.random.randint(50, 500, 30),
        "comments": np.random.randint(5, 50, 30),
        "shares": np.random.randint(2, 30, 30),
        "impressions": np.random.randint(1000, 10000, 30)
    })
    mapping5 = detect_columns(num_only_df)
    clean5, _ = clean_dataset(num_only_df, mapping5)
    engine5 = AnalyticsEngine(clean5, mapping5)
    res5 = engine5.run_full_pipeline(n_clusters=3)
    
    assert res5["text_analytics"]["available"] is False
    assert res5["clustering"]["available"] is True
    assert len(res5["clustering"]["profiles"]) == 3
    print("  -> PASSED: Clustering succeeded; missing text handled gracefully without crash.")

    # ---------------------------------------------------------
    # TEST 6: Empty or Invalid Data
    # ---------------------------------------------------------
    print("\n[TEST 6] Testing empty DataFrame safety...")
    empty_df = pd.DataFrame()
    quality6 = assess_data_quality(empty_df)
    assert quality6["total_rows"] == 0
    clean6, _ = clean_dataset(empty_df, {})
    engine6 = AnalyticsEngine(clean6, {})
    res6 = engine6.run_full_pipeline(n_clusters=3)
    assert res6["engagement_metrics"]["total_posts"] == 0
    assert res6["clustering"]["available"] is False
    print("  -> PASSED: Empty data handled safely without uncaught exceptions.")

    # ---------------------------------------------------------
    # TEST 7: SQLite Persistence Verification
    # ---------------------------------------------------------
    print("\n[TEST 7] Testing SQLite persistence and history retrieval...")
    ds_id = register_dataset(
        filename="test_dataset.csv",
        filepath="data/test_dataset.csv",
        row_count=100,
        col_count=5,
        file_size_kb=24.5,
        detected_columns={"platform": "platform"},
        cleaning_summary={"strategy_applied": "impute_sensible"}
    )
    assert ds_id > 0
    run_id = record_analysis_run(ds_id, "test_run", {"test": True}, "SUCCESS", 0.05)
    assert run_id > 0
    save_analysis_results(run_id, ds_id, {"status": "all_good"})
    
    hist = get_analysis_history(limit=5)
    assert len(hist) > 0
    assert hist[0]["run_id"] == run_id
    print("  -> PASSED: SQLite database operations verified.")

    print("\n" + "=" * 60)
    print("ALL 7 TEST SUITES PASSED SUCCESSFULLY (100% SUCCESS RATE)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
