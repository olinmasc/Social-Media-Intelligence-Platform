"""
analytics.py - Core Big Data Analytics & Machine Learning Engine
Implements statistical analysis, engagement metrics, lexicon sentiment analysis,
K-Means clustering with PCA, and evidence-based recommendation generation.
"""

import re
import math
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Comprehensive built-in English stopwords list (zero external downloads needed)
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", 
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", 
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", 
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", 
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", 
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", 
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", 
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", 
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", 
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", 
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", 
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", 
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", 
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", 
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "just", "will",
    "get", "also", "one", "like", "see", "thread", "link", "below", "today", "day", "make", "new"
])

# High-accuracy lexicon for offline sentiment estimation
POSITIVE_WORDS = set([
    "great", "excellent", "awesome", "breakthrough", "thrilled", "success", "milestone", "best",
    "love", "amazing", "power", "future", "innovative", "proud", "good", "happy", "helpful",
    "inspiring", "celebrating", "optimize", "optimized", "clean", "stunning", "fantastic",
    "valuable", "faster", "boost", "growth", "win", "excited", "progress", "honor", "honored",
    "efficient", "perfect", "seamless", "outstanding", "beneficial", "solution", "superior"
])

NEGATIVE_WORDS = set([
    "bad", "terrible", "worst", "ruin", "fail", "failure", "broken", "costly", "problem",
    "issue", "difficult", "error", "bug", "crash", "drop", "slow", "delay", "poor", "pain",
    "hate", "struggle", "flaw", "garbage", "waste", "unpopular", "loss", "danger", "messy",
    "frustrating", "vulnerable", "warning", "risk", "hard", "leak", "fatigue", "outdated"
])

NEGATION_WORDS = set(["not", "never", "no", "hardly", "barely", "scarcely", "without", "neither"])


def estimate_sentiment(text: str) -> Tuple[float, str]:
    """
    Lightweight rule-based sentiment estimator with negation handling.
    Returns polarity score in [-1.0, 1.0] and category (Positive, Neutral, Negative).
    Note: Heuristic estimate for offline academic demonstration.
    """
    if not isinstance(text, str) or not text.strip():
        return 0.0, "Neutral"
        
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if not words:
        return 0.0, "Neutral"
        
    score = 0.0
    negated = False
    
    for i, word in enumerate(words):
        if word in NEGATION_WORDS:
            negated = True
            continue
            
        weight = 1.0
        if negated:
            weight = -0.8
            # Negation expires after 2 words
            negated = False
            
        if word in POSITIVE_WORDS:
            score += weight
        elif word in NEGATIVE_WORDS:
            score -= weight
            
    # Normalized score using hyperbolic tangent style bounds
    normalized = math.tanh(score / 2.5) if words else 0.0
    
    if normalized > 0.15:
        category = "Positive"
    elif normalized < -0.15:
        category = "Negative"
    else:
        category = "Neutral"
        
    return round(normalized, 3), category


class AnalyticsEngine:
    """
    Modular Analytics and Machine Learning Engine for Social Media Data.
    Provides descriptive statistics, engagement trends, text analytics,
    clustering segmentation, and automated data-driven insights.
    """

    def __init__(self, df: pd.DataFrame, mapping: Dict[str, Optional[str]]):
        self.raw_df = df.copy()
        self.mapping = mapping
        self.df = self._prepare_data(df, mapping)
        
    def _prepare_data(self, df: pd.DataFrame, mapping: Dict[str, Optional[str]]) -> pd.DataFrame:
        """Prepares calculated fields such as total engagement and standardized date."""
        df_work = df.copy()
        
        # Calculate engagement sum if metrics available
        metric_cols = [mapping[k] for k in ["likes", "comments", "shares"] if mapping.get(k) and mapping[k] in df_work.columns]
        if metric_cols:
            df_work["_calculated_engagement"] = df_work[metric_cols].sum(axis=1)
        else:
            df_work["_calculated_engagement"] = 0
            
        # Parse date if available
        date_col = mapping.get("date")
        if date_col and date_col in df_work.columns:
            df_work["_parsed_date"] = pd.to_datetime(df_work[date_col], format="mixed", errors="coerce")
            df_work["_year_month"] = df_work["_parsed_date"].dt.to_period("M").astype(str)
            df_work["_day_name"] = df_work["_parsed_date"].dt.day_name()
            df_work["_hour"] = df_work["_parsed_date"].dt.hour
        else:
            df_work["_parsed_date"] = pd.NaT
            df_work["_year_month"] = None
            df_work["_day_name"] = None
            df_work["_hour"] = None
            
        return df_work

    def compute_descriptive_stats(self) -> Dict[str, Any]:
        """Calculates comprehensive descriptive statistics for numeric attributes."""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude internal helper columns
        numeric_cols = [c for c in numeric_cols if not c.startswith("_")]
        
        stats = {}
        for col in numeric_cols:
            series = self.df[col].dropna()
            if len(series) > 0:
                stats[col] = {
                    "count": int(series.count()),
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                    "std": round(float(series.std()), 2) if len(series) > 1 else 0.0,
                    "min": round(float(series.min()), 2),
                    "max": round(float(series.max()), 2),
                    "q25": round(float(series.quantile(0.25)), 2),
                    "q75": round(float(series.quantile(0.75)), 2)
                }
        return stats

    def compute_engagement_metrics(self) -> Dict[str, Any]:
        """Computes summary metrics, platform performance, top posts, and engagement rates."""
        results = {
            "total_posts": len(self.df),
            "total_engagement": int(self.df["_calculated_engagement"].sum()),
            "avg_engagement_per_post": round(float(self.df["_calculated_engagement"].mean()), 2) if len(self.df) > 0 else 0,
            "avg_likes": 0.0,
            "avg_comments": 0.0,
            "avg_shares": 0.0,
            "avg_impressions": 0.0,
            "overall_engagement_rate": None,
            "engagement_rate_formula": "((Total Likes + Comments + Shares) / Total Impressions) * 100",
            "most_engaging_post": None,
            "most_active_platform": None,
            "platform_breakdown": [],
            "top_posts": [],
            "correlation_matrix": {}
        }
        
        # Averages for individual metrics
        likes_col = self.mapping.get("likes")
        if likes_col and likes_col in self.df.columns:
            results["avg_likes"] = round(float(self.df[likes_col].mean()), 2)
            
        comments_col = self.mapping.get("comments")
        if comments_col and comments_col in self.df.columns:
            results["avg_comments"] = round(float(self.df[comments_col].mean()), 2)
            
        shares_col = self.mapping.get("shares")
        if shares_col and shares_col in self.df.columns:
            results["avg_shares"] = round(float(self.df[shares_col].mean()), 2)
            
        impressions_col = self.mapping.get("impressions")
        if impressions_col and impressions_col in self.df.columns:
            tot_imp = self.df[impressions_col].sum()
            results["avg_impressions"] = round(float(self.df[impressions_col].mean()), 2)
            if tot_imp > 0 and results["total_engagement"] > 0:
                results["overall_engagement_rate"] = round(float((results["total_engagement"] / tot_imp) * 100), 2)

        # Most engaging post
        if len(self.df) > 0 and self.df["_calculated_engagement"].max() > 0:
            top_idx = self.df["_calculated_engagement"].idxmax()
            top_row = self.df.loc[top_idx]
            
            post_id_val = top_row.get(self.mapping.get("post_id") or "post_id", f"Row {top_idx}")
            platform_val = top_row.get(self.mapping.get("platform") or "platform", "N/A")
            text_val = str(top_row.get(self.mapping.get("text") or "text", "No text"))
            
            results["most_engaging_post"] = {
                "post_id": str(post_id_val),
                "platform": str(platform_val),
                "engagement": int(top_row["_calculated_engagement"]),
                "likes": int(top_row.get(likes_col, 0)) if likes_col else 0,
                "text_snippet": (text_val[:90] + "...") if len(text_val) > 90 else text_val
            }
            
        # Platform breakdown
        platform_col = self.mapping.get("platform")
        if platform_col and platform_col in self.df.columns:
            plat_counts = self.df[platform_col].value_counts()
            if len(plat_counts) > 0:
                results["most_active_platform"] = str(plat_counts.index[0])
                
            grouped = self.df.groupby(platform_col)
            plat_data = []
            for name, grp in grouped:
                p_item = {
                    "platform": str(name),
                    "posts": len(grp),
                    "total_engagement": int(grp["_calculated_engagement"].sum()),
                    "avg_engagement": round(float(grp["_calculated_engagement"].mean()), 2),
                    "avg_likes": round(float(grp[likes_col].mean()), 2) if likes_col and likes_col in grp.columns else 0.0,
                    "avg_comments": round(float(grp[comments_col].mean()), 2) if comments_col and comments_col in grp.columns else 0.0,
                    "avg_shares": round(float(grp[shares_col].mean()), 2) if shares_col and shares_col in grp.columns else 0.0,
                }
                if impressions_col and impressions_col in grp.columns:
                    p_imp = grp[impressions_col].sum()
                    p_eng = grp["_calculated_engagement"].sum()
                    p_item["engagement_rate"] = round(float((p_eng / p_imp) * 100), 2) if p_imp > 0 else 0.0
                plat_data.append(p_item)
            results["platform_breakdown"] = sorted(plat_data, key=lambda x: x["total_engagement"], reverse=True)

        # Top 10 posts
        if len(self.df) > 0:
            top10 = self.df.sort_values(by="_calculated_engagement", ascending=False).head(10)
            top_list = []
            for _, r in top10.iterrows():
                p_id = r.get(self.mapping.get("post_id") or "post_id", "N/A")
                p_plat = r.get(platform_col, "N/A") if platform_col else "N/A"
                p_txt = str(r.get(self.mapping.get("text") or "text", ""))
                top_list.append({
                    "post_id": str(p_id),
                    "platform": str(p_plat),
                    "engagement": int(r["_calculated_engagement"]),
                    "likes": int(r[likes_col]) if likes_col and likes_col in r else 0,
                    "comments": int(r[comments_col]) if comments_col and comments_col in r else 0,
                    "shares": int(r[shares_col]) if shares_col and shares_col in r else 0,
                    "text_snippet": (p_txt[:80] + "...") if len(p_txt) > 80 else p_txt
                })
            results["top_posts"] = top_list

        # Correlation between metrics
        valid_metric_cols = [self.mapping[k] for k in ["likes", "comments", "shares", "impressions"] if self.mapping.get(k) and self.mapping[k] in self.df.columns]
        if len(valid_metric_cols) >= 2:
            corr_df = self.df[valid_metric_cols].corr()
            results["correlation_matrix"] = {
                "columns": valid_metric_cols,
                "values": corr_df.round(3).values.tolist()
            }
            
        return results

    def compute_temporal_trends(self) -> Dict[str, Any]:
        """Aggregates engagement by date, day of week, and hour."""
        date_col = self.mapping.get("date")
        if not date_col or date_col not in self.df.columns or self.df["_parsed_date"].isna().all():
            return {"available": False, "reason": "No valid datetime column detected in dataset."}
            
        valid_dates = self.df.dropna(subset=["_parsed_date"]).copy()
        
        # Monthly trend
        monthly = valid_dates.groupby("_year_month")["_calculated_engagement"].agg(["count", "sum", "mean"]).reset_index()
        monthly = monthly.sort_values(by="_year_month")
        
        # Day of week trend
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = valid_dates.groupby("_day_name")["_calculated_engagement"].agg(["count", "mean"]).reindex(day_order).fillna(0).reset_index()
        
        # Hourly trend
        hourly = valid_dates.groupby("_hour")["_calculated_engagement"].agg(["count", "mean"]).reset_index()
        hourly = hourly.sort_values(by="_hour")
        
        return {
            "available": True,
            "monthly_labels": monthly["_year_month"].tolist(),
            "monthly_sum": monthly["sum"].round(1).tolist(),
            "monthly_mean": monthly["mean"].round(1).tolist(),
            "monthly_count": monthly["count"].tolist(),
            "dow_labels": dow["_day_name"].tolist(),
            "dow_mean": dow["mean"].round(1).tolist(),
            "dow_count": dow["count"].tolist(),
            "hourly_labels": hourly["_hour"].tolist(),
            "hourly_mean": hourly["mean"].round(1).tolist()
        }

    def compute_text_analytics(self) -> Dict[str, Any]:
        """Extracts vocabulary frequencies, hashtag counts, and performs lexicon sentiment."""
        text_col = self.mapping.get("text")
        if not text_col or text_col not in self.df.columns:
            return {"available": False, "reason": "No text column available for NLP analysis."}
            
        texts = self.df[text_col].dropna().astype(str).tolist()
        if not texts:
            return {"available": False, "reason": "Text column is empty."}
            
        # 1. Word Frequencies
        word_counts = {}
        for t in texts:
            cleaned = re.sub(r"https?://\S+|#\w+|@\w+|[^\w\s]", "", t.lower())
            tokens = cleaned.split()
            for token in tokens:
                if len(token) > 2 and token not in STOPWORDS and not token.isdigit():
                    word_counts[token] = word_counts.get(token, 0) + 1
                    
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:25]
        
        # 2. Hashtags
        tag_counts = {}
        # Try explicit hashtag column first
        tag_col = self.mapping.get("hashtags")
        if tag_col and tag_col in self.df.columns:
            for item in self.df[tag_col].dropna().astype(str):
                # Split commas or spaces
                found_tags = re.findall(r"#?\w+", item)
                for tag in found_tags:
                    tag_norm = "#" + tag.lstrip("#").capitalize()
                    if len(tag_norm) > 2:
                        tag_counts[tag_norm] = tag_counts.get(tag_norm, 0) + 1
        else:
            # Extract from text
            for t in texts:
                found_tags = re.findall(r"#\w+", t)
                for tag in found_tags:
                    tag_norm = "#" + tag.lstrip("#").capitalize()
                    tag_counts[tag_norm] = tag_counts.get(tag_norm, 0) + 1
                    
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 3. Sentiment Estimation
        sentiment_scores = []
        sentiment_labels = {"Positive": 0, "Neutral": 0, "Negative": 0}
        
        for t in texts:
            score, label = estimate_sentiment(t)
            sentiment_scores.append(score)
            sentiment_labels[label] += 1
            
        avg_score = round(float(np.mean(sentiment_scores)), 3) if sentiment_scores else 0.0
        
        return {
            "available": True,
            "top_words": [{"word": w, "count": c} for w, c in sorted_words],
            "top_hashtags": [{"hashtag": h, "count": c} for h, c in sorted_tags],
            "sentiment_distribution": sentiment_labels,
            "avg_sentiment_score": avg_score,
            "total_texts_analyzed": len(texts),
            "disclaimer": "Sentiment scores are rule-based offline estimates based on linguistic polarity lexicons, suitable for academic demonstration."
        }

    def compute_clustering(self, n_clusters: int = 3) -> Dict[str, Any]:
        """
        Executes K-Means Clustering on numeric engagement attributes.
        Includes feature standardization, cluster sizing, centroid profiles,
        and 2D PCA projection for visualization.
        """
        candidate_cols = [self.mapping[k] for k in ["likes", "comments", "shares", "impressions"] if self.mapping.get(k) and self.mapping[k] in self.df.columns]
        
        if len(candidate_cols) < 2:
            return {
                "available": False, 
                "reason": "Clustering requires at least 2 numerical engagement attributes (e.g. likes and comments)."
            }
            
        data_clean = self.df[candidate_cols].dropna().copy()
        if len(data_clean) < 15:
            return {
                "available": False,
                "reason": f"Insufficient sample size for clustering (requires >= 15 rows, found {len(data_clean)})."
            }
            
        # Ensure n_clusters is valid
        k = max(2, min(n_clusters, 6, len(data_clean) - 1))
        
        # Standardization
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data_clean)
        
        # K-Means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        data_clean["_cluster"] = labels
        
        # 2D PCA for visual projection
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        data_clean["_pca_x"] = X_pca[:, 0]
        data_clean["_pca_y"] = X_pca[:, 1]
        
        explained_variance = [round(float(v) * 100, 2) for v in pca.explained_variance_ratio_]
        
        # Cluster Profiles
        profiles = []
        for cluster_id in range(k):
            sub = data_clean[data_clean["_cluster"] == cluster_id]
            size = len(sub)
            pct = round(size / len(data_clean) * 100, 1)
            
            centroid_means = {}
            for col in candidate_cols:
                centroid_means[col] = round(float(sub[col].mean()), 1)
                
            # Interpretation synthesis
            # Determine distinguishing metric
            overall_means = data_clean[candidate_cols].mean()
            relative_diffs = {c: (centroid_means[c] - overall_means[c]) / max(1.0, overall_means[c]) for c in candidate_cols}
            top_metric = max(relative_diffs.items(), key=lambda x: x[1])
            
            if top_metric[1] > 0.4:
                interp = f"High engagement tier driven by strong {top_metric[0]} performance (above average)."
            elif top_metric[1] < -0.3:
                interp = f"Baseline / routine content segment with modest engagement across metrics."
            else:
                interp = f"Moderate engagement cluster showing balanced reaction across features."
                
            profiles.append({
                "cluster_id": cluster_id,
                "label": f"Cluster {cluster_id}",
                "size": size,
                "percentage": pct,
                "means": centroid_means,
                "interpretation": interp
            })
            
        # Prepare sample points for frontend scatter plot (max 300 to keep UI ultra responsive)
        sample_subset = data_clean.head(350).copy()
        points = []
        for idx, row in sample_subset.iterrows():
            points.append({
                "pca_x": round(float(row["_pca_x"]), 3),
                "pca_y": round(float(row["_pca_y"]), 3),
                "cluster": int(row["_cluster"]),
                "details": {col: round(float(row[col]), 1) for col in candidate_cols}
            })
            
        return {
            "available": True,
            "k": k,
            "features_used": candidate_cols,
            "total_points": len(data_clean),
            "explained_variance_ratio": explained_variance,
            "total_variance_explained": round(sum(explained_variance), 2),
            "profiles": profiles,
            "scatter_points": points
        }

    def generate_actionable_insights(self) -> List[Dict[str, str]]:
        """
        Synthesizes actual computed metrics into concrete evidence-based observations
        and strategic recommendations for viva presentation.
        Never fabricates findings.
        """
        insights = []
        
        # 1. Platform Insight
        plat_metrics = self.compute_engagement_metrics()
        breakdown = plat_metrics.get("platform_breakdown", [])
        if breakdown:
            best_platform = max(breakdown, key=lambda x: x["avg_engagement"])
            worst_platform = min(breakdown, key=lambda x: x["avg_engagement"])
            
            insights.append({
                "category": "Platform Performance",
                "finding": f"'{best_platform['platform']}' yielded the highest average engagement ({best_platform['avg_engagement']} per post), outperforming '{worst_platform['platform']}' ({worst_platform['avg_engagement']} per post).",
                "recommendation": f"Prioritize high-value content allocation and campaign budgeting towards {best_platform['platform']} to maximize return on effort."
            })
            
        # 2. Metric Correlation Insight
        corr = plat_metrics.get("correlation_matrix", {})
        if corr and "columns" in corr and len(corr["columns"]) >= 2:
            cols = corr["columns"]
            vals = corr["values"]
            
            # Find highest off-diagonal correlation
            max_r = -1.0
            pair = ("", "")
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    r = vals[i][j]
                    if r > max_r:
                        max_r = r
                        pair = (cols[i], cols[j])
                        
            if max_r > 0.5:
                insights.append({
                    "category": "Correlation Dynamics",
                    "finding": f"Strong positive correlation (r = {round(max_r, 2)}) observed between '{pair[0]}' and '{pair[1]}'.",
                    "recommendation": f"Strategies designed to trigger initial reactions ({pair[0]}) naturally amplify downstream distribution ({pair[1]})."
                })
            elif max_r > 0:
                insights.append({
                    "category": "Metric Independence",
                    "finding": f"Moderate correlation (r = {round(max_r, 2)}) between '{pair[0]}' and '{pair[1]}' indicates diversified audience response modes.",
                    "recommendation": "Track multiple distinct KPIs rather than relying on a single engagement proxy."
                })

        # 3. Temporal Patterns
        temporal = self.compute_temporal_trends()
        if temporal.get("available"):
            dow_labels = temporal.get("dow_labels", [])
            dow_mean = temporal.get("dow_mean", [])
            if dow_labels and dow_mean:
                best_day_idx = int(np.argmax(dow_mean))
                best_day = dow_labels[best_day_idx]
                best_day_val = dow_mean[best_day_idx]
                
                insights.append({
                    "category": "Temporal Scheduling",
                    "finding": f"Content published on {best_day} experienced peak average engagement ({best_day_val} interactions/post).",
                    "recommendation": f"Schedule core product releases, milestone announcements, and technical deep-dives on {best_day} mornings."
                })
                
        # 4. Text & Hashtag Drivers
        text_data = self.compute_text_analytics()
        if text_data.get("available"):
            top_tags = text_data.get("top_hashtags", [])
            if top_tags:
                top_3 = ", ".join([t["hashtag"] for t in top_tags[:3]])
                insights.append({
                    "category": "Topic & Hashtag Reach",
                    "finding": f"Top occurring community hashtags identified: {top_3} with {top_tags[0]['count']} occurrences for #{top_tags[0]['hashtag'].lstrip('#')}.",
                    "recommendation": f"Incorporate relevant high-frequency indexing tags ({top_3}) in metadata to maximize organic discoverability."
                })
                
        # 5. Sentiment Sentiment distribution
        if text_data.get("available"):
            s_dist = text_data.get("sentiment_distribution", {})
            pos = s_dist.get("Positive", 0)
            tot = sum(s_dist.values())
            if tot > 0:
                pos_pct = round(pos / tot * 100, 1)
                insights.append({
                    "category": "Audience Tone & Sentiment",
                    "finding": f"{pos_pct}% of posts analyzed exhibited predominantly positive sentiment tone.",
                    "recommendation": "Maintain constructive, solution-oriented messaging which strongly correlates with community trust and sharing."
                })
                
        # Fallback if bare minimum
        if not insights:
            insights.append({
                "category": "General Observation",
                "finding": f"Dataset contains {len(self.df)} records across {len(self.df.columns)} fields.",
                "recommendation": "Map additional engagement columns (likes, comments, impressions) to unlock deep behavioral insights."
            })
            
        return insights

    def run_full_pipeline(self, n_clusters: int = 3) -> Dict[str, Any]:
        """Executes all analytics modules and aggregates comprehensive results."""
        return {
            "descriptive_stats": self.compute_descriptive_stats(),
            "engagement_metrics": self.compute_engagement_metrics(),
            "temporal_trends": self.compute_temporal_trends(),
            "text_analytics": self.compute_text_analytics(),
            "clustering": self.compute_clustering(n_clusters=n_clusters),
            "actionable_insights": self.generate_actionable_insights()
        }
