"""
app.py - Social Media Analytics Dashboard
Interactive Data Analysis and Machine Learning Visualization Platform
Built with Streamlit, Plotly, Pandas, Scikit-learn, and SQLite.
Designed for Big Data Analytics (BDA) mini-project examination and viva demonstration.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils import (
    detect_columns,
    assess_data_quality,
    clean_dataset,
    format_number,
    get_feature_availability,
    COLUMN_SYNONYMS
)
from analytics import AnalyticsEngine
from database import (
    init_db,
    register_dataset,
    record_analysis_run,
    save_analysis_results,
    get_analysis_history,
    get_analysis_result_by_run_id,
    clear_all_history
)

def inject_custom_css():
    """Injects custom CSS for modern Dark Navy executive aesthetics."""
    st.markdown("""
    <style>
        /* Main Dark Theme Styling */
        .stApp {
            background-color: #0b0f19;
            color: #f1f5f9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
        }
        
        /* Metrics Card Styling */
        .metric-card {
            background: linear-gradient(135deg, #1e293b 0%, #172554 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            margin-bottom: 16px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .metric-card:hover {
            border-color: #14b8a6;
            transform: translateY(-2px);
        }
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #38bdf8;
            line-height: 1.2;
        }
        .metric-sub {
            font-size: 0.78rem;
            color: #cbd5e1;
            margin-top: 6px;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 1.35rem;
            font-weight: 700;
            color: #f8fafc;
            border-left: 4px solid #14b8a6;
            padding-left: 12px;
            margin-top: 24px;
            margin-bottom: 18px;
        }
        
        /* Health Badge */
        .health-pill {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.85rem;
        }
        .health-good {
            background-color: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid #059669;
        }
        .health-warn {
            background-color: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            border: 1px solid #d97706;
        }
        
        /* Audit Item */
        .audit-box {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 12px 16px;
            border-left: 3px solid #06b6d4;
            margin-bottom: 8px;
            font-size: 0.88rem;
            color: #cbd5e1;
        }
    </style>
    """, unsafe_allow_html=True)


def init_session_state():
    """Initializes Streamlit session states for dataset and analytics."""
    init_db()
    if "df" not in st.session_state:
        st.session_state.df = None
    if "cleaned_df" not in st.session_state:
        st.session_state.cleaned_df = None
    if "mapping" not in st.session_state:
        st.session_state.mapping = {}
    if "quality_report" not in st.session_state:
        st.session_state.quality_report = None
    if "cleaning_summary" not in st.session_state:
        st.session_state.cleaning_summary = None
    if "analytics_results" not in st.session_state:
        st.session_state.analytics_results = None
    if "dataset_name" not in st.session_state:
        st.session_state.dataset_name = None
    if "dataset_id" not in st.session_state:
        st.session_state.dataset_id = None
    if "last_run_id" not in st.session_state:
        st.session_state.last_run_id = None


def load_dataset_into_state(df: pd.DataFrame, filename: str, filepath: str = ""):
    """Loads a DataFrame, detects columns, profiles data quality, and initializes state."""
    st.session_state.df = df
    st.session_state.dataset_name = filename
    mapping = detect_columns(df)
    st.session_state.mapping = mapping
    st.session_state.quality_report = assess_data_quality(df)
    
    clean_df, summary = clean_dataset(df, mapping, drop_duplicates_flag=True, missing_strategy="impute_sensible")
    st.session_state.cleaned_df = clean_df
    st.session_state.cleaning_summary = summary
    
    file_size_kb = round(df.memory_usage(deep=True).sum() / 1024, 2)
    ds_id = register_dataset(
        filename=filename,
        filepath=filepath or f"data/{filename}",
        row_count=len(df),
        col_count=len(df.columns),
        file_size_kb=file_size_kb,
        detected_columns=mapping,
        cleaning_summary=summary
    )
    st.session_state.dataset_id = ds_id
    
    engine = AnalyticsEngine(clean_df, mapping)
    start_t = time.time()
    results = engine.run_full_pipeline(n_clusters=3)
    exec_time = round(time.time() - start_t, 3)
    
    run_id = record_analysis_run(ds_id, "full", {"n_clusters": 3}, "SUCCESS", exec_time)
    save_analysis_results(run_id, ds_id, results)
    
    st.session_state.analytics_results = results
    st.session_state.last_run_id = run_id


def render_dashboard_overview():
    st.title("Social Media Analytics Executive Dashboard")
    st.markdown("High-level multi-platform KPI metrics, engagement distribution, and sentiment indicators.")
    
    if st.session_state.cleaned_df is None:
        st.info("Welcome! To begin the demonstration, please load the sample dataset or upload a CSV file.")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Load Pre-built 700 Post Sample Dataset", use_container_width=True, type="primary"):
                sample_path = "data/sample_social_media.csv"
                if not os.path.exists(sample_path):
                    from generate_sample_data import generate_social_media_dataset
                    generate_social_media_dataset()
                sample_df = pd.read_csv(sample_path)
                load_dataset_into_state(sample_df, "sample_social_media.csv", sample_path)
                st.rerun()
        with col_b:
            st.markdown("Or navigate to **'Dataset Upload & Quality'** in the sidebar to upload your custom CSV.")
        return
        
    df = st.session_state.cleaned_df
    mapping = st.session_state.mapping
    results = st.session_state.analytics_results
    
    with st.expander("Interactive Filters & Cross-Filter Controls", expanded=False):
        f_col1, f_col2 = st.columns(2)
        platform_col = mapping.get("platform")
        date_col = mapping.get("date")
        
        filtered_df = df.copy()
        
        if platform_col and platform_col in df.columns:
            all_platforms = ["All"] + sorted(list(df[platform_col].dropna().unique()))
            selected_plat = f_col1.selectbox("Filter by Platform", all_platforms)
            if selected_plat != "All":
                filtered_df = filtered_df[filtered_df[platform_col] == selected_plat]
                
        if date_col and date_col in df.columns:
            try:
                min_date = pd.to_datetime(df[date_col]).min().date()
                max_date = pd.to_datetime(df[date_col]).max().date()
                date_range = f_col2.date_input("Date Range", [min_date, max_date])
                if len(date_range) == 2:
                    start_d, end_d = date_range
                    mask = (pd.to_datetime(filtered_df[date_col]).dt.date >= start_d) & (pd.to_datetime(filtered_df[date_col]).dt.date <= end_d)
                    filtered_df = filtered_df[mask]
            except Exception:
                f_col2.caption("Date filtering not available for current format.")
                
        filtered_engine = AnalyticsEngine(filtered_df, mapping)
        filtered_results = filtered_engine.run_full_pipeline(n_clusters=3)
        eng_m = filtered_results["engagement_metrics"]
        text_m = filtered_results["text_analytics"]
    
    if 'eng_m' not in locals():
        eng_m = results["engagement_metrics"]
        text_m = results["text_analytics"]
        filtered_df = df

    # ROW 1: CORE KPI METRICS CARDS
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Posts</div>
            <div class="metric-value">{format_number(eng_m['total_posts'], 0)}</div>
            <div class="metric-sub">Analyzed records</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Engagement</div>
            <div class="metric-value">{format_number(eng_m['total_engagement'], 1)}</div>
            <div class="metric-sub">Likes + Comments + Shares</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Engagement</div>
            <div class="metric-value">{format_number(eng_m['avg_engagement_per_post'], 1)}</div>
            <div class="metric-sub">Interactions / post</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        rate_display = f"{eng_m['overall_engagement_rate']}%" if eng_m['overall_engagement_rate'] is not None else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Engagement Rate</div>
            <div class="metric-value">{rate_display}</div>
            <div class="metric-sub">(Eng / Impressions) * 100</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col5:
        top_plat = eng_m.get("most_active_platform") or "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Most Active Platform</div>
            <div class="metric-value" style="font-size: 1.4rem;">{top_plat}</div>
            <div class="metric-sub">By post frequency</div>
        </div>
        """, unsafe_allow_html=True)

    # ROW 2: DETAILED INTERACTION METRICS
    sub_col1, sub_col2, sub_col3, sub_col4 = st.columns(4)
    with sub_col1:
        st.caption(f"Avg Likes: {format_number(eng_m['avg_likes'])}")
    with sub_col2:
        st.caption(f"Avg Comments: {format_number(eng_m['avg_comments'])}")
    with sub_col3:
        st.caption(f"Avg Shares: {format_number(eng_m['avg_shares'])}")
    with sub_col4:
        st.caption(f"Avg Impressions: {format_number(eng_m.get('avg_impressions'))}")

    st.markdown("---")

    # ROW 3: INTERACTIVE CHARTS
    chart_col1, chart_col2 = st.columns([6, 5])
    
    with chart_col1:
        st.markdown('<div class="section-header">Platform Engagement Comparison</div>', unsafe_allow_html=True)
        breakdown = eng_m.get("platform_breakdown", [])
        if breakdown:
            plat_df = pd.DataFrame(breakdown)
            fig_plat = px.bar(
                plat_df,
                x="platform",
                y="total_engagement",
                color="platform",
                text="total_engagement",
                color_discrete_sequence=["#14b8a6", "#06b6d4", "#3b82f6", "#f59e0b", "#ec4899"],
                labels={"total_engagement": "Total Engagement", "platform": "Platform"},
                template="plotly_dark"
            )
            fig_plat.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig_plat.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=False,
                height=340
            )
            st.plotly_chart(fig_plat, use_container_width=True)
        else:
            st.info("Platform comparison requires a mapped 'platform' column.")
            
    with chart_col2:
        st.markdown('<div class="section-header">Estimated Sentiment Distribution</div>', unsafe_allow_html=True)
        if text_m.get("available"):
            sent_dist = text_m["sentiment_distribution"]
            sent_df = pd.DataFrame([
                {"Sentiment": k, "Count": v} for k, v in sent_dist.items()
            ])
            color_map = {"Positive": "#10b981", "Neutral": "#64748b", "Negative": "#ef4444"}
            fig_sent = px.pie(
                sent_df,
                values="Count",
                names="Sentiment",
                color="Sentiment",
                color_discrete_map=color_map,
                hole=0.55,
                template="plotly_dark"
            )
            fig_sent.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=340
            )
            st.plotly_chart(fig_sent, use_container_width=True)
        else:
            st.info("Sentiment breakdown requires a mapped 'text' column.")

    # ROW 4: TEMPORAL ENGAGEMENT TIMELINE
    st.markdown('<div class="section-header">Engagement Trajectory Over Time</div>', unsafe_allow_html=True)
    temporal = filtered_results.get("temporal_trends", {})
    if temporal.get("available") and temporal.get("monthly_labels"):
        t_df = pd.DataFrame({
            "Month": temporal["monthly_labels"],
            "Total Engagement": temporal["monthly_sum"],
            "Post Count": temporal["monthly_count"]
        })
        fig_time = px.line(
            t_df,
            x="Month",
            y="Total Engagement",
            markers=True,
            line_shape="spline",
            template="plotly_dark",
            color_discrete_sequence=["#38bdf8"]
        )
        fig_time.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=20),
            height=280
        )
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.caption("Temporal trend line chart requires a parsed date column.")




def render_upload_and_quality():
    st.title("Dataset Upload, Automated Detection & Quality Profiling")
    st.markdown("Upload any social media CSV. Our ingestion engine maps column variations, validates data types, and logs all cleaning steps.")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file to analyze",
        type=["csv"],
        help="Upload social media posts CSV. Columns like platform, likes, comments, date, and text will be mapped automatically."
    )
    
    if uploaded_file is not None:
        try:
            raw_upload_df = pd.read_csv(uploaded_file)
            st.success(f"Successfully read {uploaded_file.name} ({len(raw_upload_df):,} rows, {len(raw_upload_df.columns)} columns)")
            
            auto_mapping = detect_columns(raw_upload_df)
            
            with st.expander("Column Synonym Mapping & Overrides", expanded=True):
                st.markdown("Verify or re-assign standard social media attributes detected in your CSV:")
                all_cols = ["(None / Skip)"] + list(raw_upload_df.columns)
                
                custom_mapping = {}
                col_slots = st.columns(3)
                
                for idx, standard_key in enumerate(COLUMN_SYNONYMS.keys()):
                    slot = col_slots[idx % 3]
                    detected_val = auto_mapping.get(standard_key)
                    default_idx = (all_cols.index(detected_val)) if detected_val in all_cols else 0
                    
                    selected_col = slot.selectbox(
                        f"Field: {standard_key.replace('_', ' ').capitalize()}",
                        all_cols,
                        index=default_idx,
                        key=f"col_map_{standard_key}"
                    )
                    custom_mapping[standard_key] = None if selected_col == "(None / Skip)" else selected_col

            st.markdown('<div class="section-header">Data Cleaning Configuration</div>', unsafe_allow_html=True)
            c_opt1, c_opt2 = st.columns(2)
            with c_opt1:
                drop_dups = st.checkbox("Drop Exact Duplicate Rows", value=True, help="Removes identical rows to avoid skewing analytics.")
            with c_opt2:
                missing_opt = st.selectbox(
                    "Missing Values Strategy",
                    [
                        ("impute_sensible", "Impute Sensibly (Median for metrics, 'Unknown' for categories)"),
                        ("drop_rows", "Drop any rows with missing values"),
                        ("keep_as_is", "Keep missing values as-is (NaN)")
                    ],
                    format_func=lambda x: x[1]
                )[0]

            quality = assess_data_quality(raw_upload_df)
            score = quality["health_score"]
            badge_class = "health-good" if score >= 80 else "health-warn"
            
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 16px; border-radius: 8px; margin: 16px 0;">
                <span style="font-size: 1.1rem; font-weight: 600;">Data Quality Health Index: </span>
                <span class="health-pill {badge_class}">{score} / 100</span>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">
                    Duplicate rows found: <b>{quality['duplicate_rows']}</b> ({quality['duplicate_pct']}%) | 
                    Columns with missing cells: <b>{quality['columns_with_missing']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Confirm & Run Analytics Pipeline", type="primary", use_container_width=True):
                clean_df, summary = clean_dataset(
                    raw_upload_df,
                    custom_mapping,
                    drop_duplicates_flag=drop_dups,
                    missing_strategy=missing_opt
                )
                
                os.makedirs("data", exist_ok=True)
                save_path = os.path.join("data", f"uploaded_{uploaded_file.name}")
                clean_df.to_csv(save_path, index=False)
                
                load_dataset_into_state(clean_df, uploaded_file.name, save_path)
                st.session_state.cleaning_summary = summary
                st.session_state.mapping = custom_mapping
                
                st.success("Analysis completed successfully. Navigate to 'Dashboard Overview' or 'In-Depth Analytics' to view results.")
                
        except Exception as e:
            st.error(f"Error reading uploaded CSV: {str(e)}")
            st.info("Please ensure the uploaded file is a valid UTF-8 formatted CSV.")

    else:
        st.markdown("""
        <div style="border: 2px dashed #334155; border-radius: 12px; padding: 40px; text-align: center; margin: 20px 0;">
            <div style="font-size: 1.2rem; font-weight: 600; color: #f8fafc;">Drag and drop your social media CSV file here</div>
            <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 6px;">Compatible with Twitter, Instagram, LinkedIn, YouTube, and Facebook exports.</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.cleaning_summary is not None:
        st.markdown('<div class="section-header">Data Cleaning Audit Trail</div>', unsafe_allow_html=True)
        st.caption("Every transformation performed by the analytics engine is explicitly audited:")
        for entry in st.session_state.cleaning_summary.get("audit_log", []):
            st.markdown(f'<div class="audit-box">• {entry}</div>', unsafe_allow_html=True)


def render_explore_raw_data():
    st.title("Exploratory Data Inspection")
    st.markdown("Inspect schema metadata, column statistics, sample rows, and missing-value distributions.")
    
    if st.session_state.cleaned_df is None:
        st.warning("No dataset active. Please load sample data from the sidebar or upload a CSV.")
        return
        
    df = st.session_state.cleaned_df
    mapping = st.session_state.mapping
    
    tab1, tab2, tab3 = st.tabs(["Data Table Viewer", "Column Data Types & Profiling", "Missing Value Diagnostics"])
    
    with tab1:
        st.markdown(f"**Showing {len(df):,} records** (Searchable and sortable):")
        st.dataframe(df, use_container_width=True, height=450)
        
    with tab2:
        st.markdown("**Attribute Data Types & Unique Counts:**")
        type_rows = []
        for col in df.columns:
            mapped_role = [k for k, v in mapping.items() if v == col]
            role_label = mapped_role[0] if mapped_role else "Unmapped"
            type_rows.append({
                "Column Name": col,
                "Inferred Role": role_label,
                "Data Type": str(df[col].dtype),
                "Non-Null Count": int(df[col].count()),
                "Unique Values": int(df[col].nunique()),
                "Sample Entry": str(df[col].dropna().iloc[0]) if len(df[col].dropna()) > 0 else "N/A"
            })
        st.table(pd.DataFrame(type_rows))
        
    with tab3:
        null_counts = df.isnull().sum()
        if null_counts.sum() == 0:
            st.success("Zero missing values detected in the active dataset.")
        else:
            null_df = pd.DataFrame({
                "Column": null_counts.index,
                "Missing Values": null_counts.values,
                "Missing Percentage": (null_counts.values / len(df) * 100).round(2)
            })
            null_df = null_df[null_df["Missing Values"] > 0]
            st.dataframe(null_df, use_container_width=True)


def render_indepth_analytics():
    st.title("Advanced Analytics Engine")
    st.markdown("Multi-dimensional statistical analysis, correlation heatmaps, NLP text mining, and hashtag distributions.")
    
    if st.session_state.analytics_results is None:
        st.warning("No active analysis. Please load or upload a dataset.")
        return
        
    results = st.session_state.analytics_results
    df = st.session_state.cleaned_df
    mapping = st.session_state.mapping
    
    tab_stat, tab_corr, tab_nlp, tab_rec = st.tabs([
        "Descriptive Statistics",
        "Metric Correlation Heatmap",
        "Text & Hashtag Mining",
        "Evidence-Based Recommendations"
    ])
    
    with tab_stat:
        st.markdown('<div class="section-header">Five-Number Summary & Metric Distributions</div>', unsafe_allow_html=True)
        stats = results.get("descriptive_stats", {})
        if stats:
            stat_df = pd.DataFrame(stats).T
            stat_df = stat_df[["count", "mean", "median", "std", "min", "q25", "q75", "max"]]
            stat_df.columns = ["Count", "Mean", "Median", "Std Dev", "Min", "25th Pct", "75th Pct", "Max"]
            st.dataframe(stat_df.style.format("{:,.2f}"), use_container_width=True)
            
            st.markdown("**Metric Distribution Histogram:**")
            num_cols = list(stats.keys())
            chosen_col = st.selectbox("Select metric to plot distribution", num_cols)
            fig_hist = px.histogram(
                df,
                x=chosen_col,
                nbins=35,
                template="plotly_dark",
                color_discrete_sequence=["#14b8a6"],
                marginal="box",
                title=f"Distribution of {chosen_col}"
            )
            fig_hist.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=350
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No numerical engagement attributes available for descriptive statistics.")

    with tab_corr:
        st.markdown('<div class="section-header">Pearson Correlation Matrix</div>', unsafe_allow_html=True)
        corr_data = results["engagement_metrics"].get("correlation_matrix", {})
        if corr_data and "columns" in corr_data:
            c_cols = corr_data["columns"]
            c_vals = corr_data["values"]
            
            fig_corr = px.imshow(
                c_vals,
                x=c_cols,
                y=c_cols,
                text_auto=True,
                color_continuous_scale="Viridis",
                template="plotly_dark",
                zmin=-1,
                zmax=1
            )
            fig_corr.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=420
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            st.markdown("""
            **Interpretation Guide:**
            - **+0.7 to +1.0**: Strong positive correlation (metrics amplify each other).
            - **+0.3 to +0.7**: Moderate relationship.
            - **-0.3 to +0.3**: Independent behavior; optimizing one metric does not directly impact the other.
            """)
        else:
            st.info("Correlation analysis requires at least 2 numerical engagement attributes (e.g. Likes, Shares, Comments).")

    with tab_nlp:
        st.markdown('<div class="section-header">Text Frequency & Community Hashtags</div>', unsafe_allow_html=True)
        text_data = results.get("text_analytics", {})
        if text_data.get("available"):
            nlp_col1, nlp_col2 = st.columns(2)
            
            with nlp_col1:
                st.markdown("**Top Occurring Words (Stopwords Filtered):**")
                words_list = text_data.get("top_words", [])[:15]
                if words_list:
                    w_df = pd.DataFrame(words_list)
                    fig_w = px.bar(
                        w_df,
                        x="count",
                        y="word",
                        orientation="h",
                        template="plotly_dark",
                        color="count",
                        color_continuous_scale="Teal",
                        labels={"count": "Frequency", "word": "Token"}
                    )
                    fig_w.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=380,
                        showlegend=False
                    )
                    st.plotly_chart(fig_w, use_container_width=True)
                else:
                    st.caption("No words extracted.")
                    
            with nlp_col2:
                st.markdown("**Top Trending Hashtags:**")
                tags_list = text_data.get("top_hashtags", [])[:15]
                if tags_list:
                    t_df = pd.DataFrame(tags_list)
                    fig_t = px.bar(
                        t_df,
                        x="count",
                        y="hashtag",
                        orientation="h",
                        template="plotly_dark",
                        color="count",
                        color_continuous_scale="Purp",
                        labels={"count": "Frequency", "hashtag": "Hashtag"}
                    )
                    fig_t.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        height=380,
                        showlegend=False
                    )
                    st.plotly_chart(fig_t, use_container_width=True)
                else:
                    st.caption("No hashtags found in text or tags column.")
                    
            st.caption(f"Note: {text_data.get('disclaimer')}")
        else:
            st.info("NLP Text analytics requires a mapped 'text' or 'caption' column.")

    with tab_rec:
        st.markdown('<div class="section-header">Automated Evidence-Based Insights</div>', unsafe_allow_html=True)
        st.markdown("Insights are algorithmically derived strictly from the active dataset:")
        
        insights = results.get("actionable_insights", [])
        for item in insights:
            st.markdown(f"""
            <div style="background-color: #1e293b; border-left: 4px solid #38bdf8; border-radius: 8px; padding: 14px 18px; margin-bottom: 14px;">
                <div style="color: #38bdf8; font-weight: 700; font-size: 0.9rem; text-transform: uppercase;">{item['category']}</div>
                <div style="color: #f1f5f9; font-size: 1.0rem; margin: 4px 0;"><b>Observed Finding:</b> {item['finding']}</div>
                <div style="color: #34d399; font-size: 0.92rem; margin-top: 6px;"><b>Suggested Strategy:</b> {item['recommendation']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_machine_learning():
    st.title("Unsupervised Machine Learning: K-Means Post Segmentation")
    st.markdown("Discovers latent engagement tiers across posts without manual labels using K-Means and 2D PCA projection.")
    
    if st.session_state.cleaned_df is None:
        st.warning("Please load or upload a dataset to train clustering models.")
        return
        
    df = st.session_state.cleaned_df
    mapping = st.session_state.mapping
    
    col_k, col_run = st.columns([3, 1])
    with col_k:
        k_val = st.slider("Select Number of Clusters (k)", min_value=2, max_value=6, value=3, step=1)
    with col_run:
        st.write("")
        st.write("")
        recluster_btn = st.button("Retrain Model", use_container_width=True)
        
    engine = AnalyticsEngine(df, mapping)
    cluster_results = engine.compute_clustering(n_clusters=k_val)
    
    if not cluster_results.get("available"):
        st.error(f"Cannot perform clustering: {cluster_results.get('reason')}")
        return
        
    var_exp = cluster_results.get("total_variance_explained", 0.0)
    st.markdown(f"""
    <div style="background-color: #1e293b; border-radius: 8px; padding: 12px 18px; margin-bottom: 18px;">
        <span style="color: #94a3b8;">Features Standardized:</span> <b>{', '.join(cluster_results['features_used'])}</b> | 
        <span style="color: #94a3b8;">Total Points:</span> <b>{cluster_results['total_points']:,}</b> | 
        <span style="color: #94a3b8;">2D PCA Variance Explained:</span> <b>{var_exp}%</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">2D PCA Spatial Projection of Content Clusters</div>', unsafe_allow_html=True)
    points = cluster_results.get("scatter_points", [])
    if points:
        scatter_df = pd.DataFrame(points)
        scatter_df["Cluster Label"] = scatter_df["cluster"].apply(lambda c: f"Cluster {c}")
        
        fig_pca = px.scatter(
            scatter_df,
            x="pca_x",
            y="pca_y",
            color="Cluster Label",
            template="plotly_dark",
            color_discrete_sequence=["#14b8a6", "#38bdf8", "#f59e0b", "#ec4899", "#8b5cf6", "#10b981"],
            labels={"pca_x": "Principal Component 1 (Reach & Scale)", "pca_y": "Principal Component 2 (Reaction Ratio)"},
            title="K-Means Content Segments Projected via PCA"
        )
        fig_pca.update_traces(marker=dict(size=8, opacity=0.85))
        fig_pca.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=450
        )
        st.plotly_chart(fig_pca, use_container_width=True)

    st.markdown('<div class="section-header">Cluster Archetypes & Centroid Feature Averages</div>', unsafe_allow_html=True)
    profiles = cluster_results.get("profiles", [])
    prof_cols = st.columns(len(profiles))
    
    for idx, p in enumerate(profiles):
        with prof_cols[idx]:
            st.markdown(f"""
            <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; height: 100%;">
                <div style="font-weight: 700; color: #38bdf8; font-size: 1.1rem;">{p['label']}</div>
                <div style="color: #94a3b8; font-size: 0.82rem; margin: 4px 0 10px 0;">{p['size']} posts ({p['percentage']}%)</div>
                <div style="font-size: 0.85rem; color: #e2e8f0; margin-bottom: 10px;"><b>Profile:</b> {p['interpretation']}</div>
                <div style="border-top: 1px solid #334155; padding-top: 8px;">
            """, unsafe_allow_html=True)
            for m_key, m_val in p["means"].items():
                st.caption(f"• **{m_key}:** {m_val:,.1f}")
            st.markdown("</div></div>", unsafe_allow_html=True)


def render_history_view():
    st.title("SQLite Persistence & Historical Analysis Runs")
    st.markdown("All dataset uploads, cleaning audits, and analytical executions are logged in relational SQLite tables.")
    
    history = get_analysis_history(limit=25)
    
    col_hist_top, col_clear = st.columns([4, 1])
    with col_hist_top:
        st.markdown(f"**Total Historical Runs Logged:** {len(history)}")
    with col_clear:
        if st.button("Clear History", use_container_width=True):
            clear_all_history()
            st.success("History cleared.")
            st.rerun()

    if not history:
        st.info("No analysis runs recorded in the database yet.")
    else:
        hist_table = []
        for h in history:
            hist_table.append({
                "Run ID": h["run_id"],
                "Dataset File": h["dataset_filename"] or "N/A",
                "Analysis Type": h["analysis_type"].upper(),
                "Status": h["status"],
                "Execution Time (s)": h["execution_time_sec"],
                "Timestamp": str(h["run_timestamp"])
            })
        st.dataframe(pd.DataFrame(hist_table), use_container_width=True)
        
        st.markdown('<div class="section-header">Inspect Past Analysis Snapshot</div>', unsafe_allow_html=True)
        selected_run_id = st.selectbox("Select Run ID to inspect details", [h["run_id"] for h in history])
        if selected_run_id:
            snap = get_analysis_result_by_run_id(selected_run_id)
            if snap and "summary_json" in snap:
                st.json(snap["summary_json"])





def main():
    st.set_page_config(
        page_title="Social Media Analytics Dashboard | BDA Project",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    inject_custom_css()
    init_session_state()

    # Sidebar Navigation without emojis
    st.sidebar.markdown("""
    <div style="padding: 10px 0 20px 0;">
        <h2 style="color: #38bdf8; margin: 0; font-size: 1.4rem;">BDA Analytics</h2>
        <p style="color: #94a3b8; font-size: 0.8rem; margin: 4px 0 0 0;">Social Media Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    nav_page = st.sidebar.radio(
        "Navigation Menu",
        [
            "Dashboard Overview",
            "Dataset Upload & Quality",
            "Explore Raw Data",
            "In-Depth Analytics",
            "Machine Learning (K-Means)",
            "Analysis History (SQLite)"
        ],
        index=0
    )

    st.sidebar.markdown("---")

    st.sidebar.markdown("**Instant Demo Mode**")
    if st.sidebar.button("Load Pre-Generated Sample Data (700 Posts)", use_container_width=True):
        sample_path = "data/sample_social_media.csv"
        if os.path.exists(sample_path):
            sample_df = pd.read_csv(sample_path)
            load_dataset_into_state(sample_df, "sample_social_media.csv", sample_path)
            st.sidebar.success("Sample dataset loaded and analyzed.")
            st.rerun()
        else:
            st.sidebar.error("Sample dataset not found. Generating now...")
            from generate_sample_data import generate_social_media_dataset
            generate_social_media_dataset()
            sample_df = pd.read_csv(sample_path)
            load_dataset_into_state(sample_df, "sample_social_media.csv", sample_path)
            st.sidebar.success("Sample generated and loaded.")
            st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Active Dataset:**")
    if st.session_state.cleaned_df is not None:
        st.sidebar.markdown(f"File: `{st.session_state.dataset_name}`")
        st.sidebar.markdown(f"Rows: **{len(st.session_state.cleaned_df):,}** | Cols: **{len(st.session_state.cleaned_df.columns)}**")
        
        avail = get_feature_availability(st.session_state.mapping)
        active_count = sum(1 for is_ok, _ in avail.values() if is_ok)
        st.sidebar.markdown(f"Features Supported: **{active_count}/{len(avail)}**")
    else:
        st.sidebar.info("No dataset currently active.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Computer Science Engineering (AI & DS)\nBig Data Analytics Mini-Project 2024-25")

    # Page Routing
    if nav_page == "Dashboard Overview":
        render_dashboard_overview()
    elif nav_page == "Dataset Upload & Quality":
        render_upload_and_quality()
    elif nav_page == "Explore Raw Data":
        render_explore_raw_data()
    elif nav_page == "In-Depth Analytics":
        render_indepth_analytics()
    elif nav_page == "Machine Learning (K-Means)":
        render_machine_learning()
    elif nav_page == "Analysis History (SQLite)":
        render_history_view()

if __name__ == "__main__":
    main()
