# Social Media Analytics Dashboard: Interactive Data Analysis and Visualization Platform
**Big Data Analytics (BDA) Mini-Project**  
*Department of Computer Science & Engineering (Specialization: AI & Data Science)*

---

## Project Overview
The **Social Media Analytics Dashboard** is an end-to-end Big Data Analytics (BDA) application engineered to ingest, profile, clean, analyze, and visualize multi-platform social media engagement metrics.

Modern businesses and content creators operate across fragmented social platforms (Twitter/X, Instagram, LinkedIn, YouTube, and Facebook). Each platform exports metrics under divergent naming schemes, with varying null rates and unstandardized scales. This platform provides:
1. **Automated Schema Normalization:** Dynamically maps heterogeneous column names (e.g. `views` vs `reach` vs `impressions`, `retweets` vs `shares`, `favs` vs `likes`).
2. **Transparent Data Quality Profiling:** Computes an automated health score, deduplicates records, handles missing data, and generates an auditable cleaning log.
3. **Statistical & Engagement Analytics:** Multi-dimensional KPI calculation, platform comparisons, time-series trends, and Pearson correlation matrices.
4. **Natural Language Processing (NLP):** Offline lexicon-based sentiment estimation, vocabulary tokenization, and community hashtag frequency analysis.
5. **Unsupervised Machine Learning:** K-Means clustering with `StandardScaler` feature normalization and 2D Principal Component Analysis (PCA) projection.
6. **Decoupled Relational Persistence:** SQLite database caching dataset pointers, analysis run metadata, and JSON snapshots.
7. **Executive Reporting:** One-click download of cleaned CSVs, JSON results, project reports, and an automated 12-slide PowerPoint presentation (`.pptx`).

---

## System Architecture & Data Pipeline

```
                                  +------------------------------------+
                                  |     CSV Ingestion & Validation     |
                                  | (Drag & Drop or 700-post Sample)   |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |   Data Quality & Cleaning Engine   |
                                  |  - Synonym mapping & Type coercion |
                                  |  - Deduplication & Null imputation |
                                  |  - Audit log generation            |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |      Pandas Analytics Engine       |
                                  +--------+-----------------+---------+
                                           |                 |
                  +------------------------+                 +------------------------+
                  |                                                                   |
                  v                                                                   v
+------------------------------------+                             +------------------------------------+
|  Statistical & Text Analytics      |                             | Machine Learning (Scikit-Learn)    |
|  - Five-number summaries           |                             |  - StandardScaler Normalization    |
|  - Engagement rate calculation     |                             |  - K-Means Post Segmentation (k)   |
|  - Correlation matrix (Pearson)    |                             |  - 2D PCA Dimensionality Reduction |
|  - Lexicon NLP Polarity Estimation |                             |  - Cluster Centroid Profiling      |
+-----------------+------------------+                             +------------------+-----------------+
                  |                                                                   |
                  +------------------------+                 +------------------------+
                                           |                 |
                                           v                 v
                                  +------------------------------------+
                                  |   Plotly Interactive Visualizer    |
                                  |  - Platform comparison bar charts  |
                                  |  - Temporal trajectory line charts |
                                  |  - Correlation heatmaps            |
                                  |  - 2D PCA cluster scatter plots    |
                                  |  - Sentiment donut charts          |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |     Streamlit Frontend (Dark)      |
                                  |  - Reactive filtering by date/plat |
                                  |  - Top-performing post callouts    |
                                  |  - Export: CSV, JSON, PPTX, MD     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |   SQLite Database (database.db)    |
                                  |  - Datasets metadata               |
                                  |  - Analysis run logs & status      |
                                  |  - Summary results JSON snapshots  |
                                  +------------------------------------+
```

### BDA Architecture Explanation for Viva
- **Why is storage decoupled?** In Big Data systems, storing raw event files directly as database cell blobs causes severe I/O degradation and storage bloat. Here, raw datasets reside in file storage while SQLite maintains schema pointers, execution telemetry, and aggregated summary snapshots.
- **How are the 4 V's demonstrated?**
  - **Volume:** Batch processing of hundreds of posts with vectorized operations scalable to millions.
  - **Velocity:** Sub-second in-memory transformations and fast UI re-rendering.
  - **Variety:** Harmonizing tabular numbers, text captions, categorical platform tags, and ISO timestamps.
  - **Veracity:** Data quality profiler computing health indices and auditing every imputed cell.

---

## Technology Stack & Justification

| Technology | Layer / Role | Technical Justification |
| :--- | :--- | :--- |
| **Python 3.10+** | Core Language | Industry-standard language for data science, AI, and big data engineering. |
| **Streamlit** | Frontend UI | Declarative Python framework allowing rapid creation of reactive dashboards with custom CSS dark-mode styling. |
| **Plotly Express** | Visualizations | Hardware-accelerated interactive charts with zooming, panning, hover tooltips, and client-side exports. |
| **Pandas & NumPy** | Analytics Engine | High-throughput vectorized matrix calculations, data cleaning, and datetime transformations. |
| **Scikit-learn** | Machine Learning | Robust implementation of `StandardScaler`, `KMeans`, and `PCA` for unsupervised clustering. |
| **SQLite3** | Embedded Database | Serverless, zero-configuration ACID-compliant SQL database embedded in standard Python. |
| **Python-PPTX** | Presentation Gen | Programmatic creation of native 16:9 widescreen PowerPoint slides for academic defense. |

---

## Repository File Structure

```
bda/
├── app.py                                # Streamlit dashboard frontend & navigation
├── analytics.py                          # Descriptive stats, engagement, lexicon sentiment, K-Means & PCA
├── database.py                           # SQLite tables, parameterized queries, and persistence helpers
├── utils.py                              # Column detection heuristics, quality profiling, and cleaning
├── generate_sample_data.py               # 700+ post reproducible synthetic dataset generator
├── generate_presentation.py              # 12-slide executive academic PowerPoint generator
├── test_suite.py                         # Automated test suite covering 7 edge cases
├── package_project.py                    # Script to bundle the project into a clean distribution ZIP
├── requirements.txt                      # Project library dependencies
├── README.md                             # Documentation, viva guide, and setup instructions
├── social_media_analytics_presentation.pptx # Generated 12-slide academic presentation
├── social_media_analytics_bda_project.zip   # Complete ready-to-submit project archive
└── data/
    ├── sample_social_media.csv           # 700 realistic social posts (Twitter, IG, LinkedIn, YT, FB)
    └── analytics_database.db             # SQLite database storing metadata and run logs
```

---

## Step-by-Step Setup Guide (macOS / Linux / Windows)

### 1. Open Terminal and Navigate to Project
```bash
cd /Users/olinmascarenhas/Desktop/bda
```

### 2. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate on macOS / Linux:
source venv/bin/activate

# (On Windows Command Prompt: venv\Scripts\activate.bat)
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Generate the Sample Dataset & Presentation
```bash
# Generate 700 realistic synthetic social media posts
python3 generate_sample_data.py

# Generate the 12-slide PowerPoint presentation
python3 generate_presentation.py
```

### 5. Run the Automated Test Suite
Verify that all 7 test suites pass before launching:
```bash
python3 test_suite.py
```

### 6. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Streamlit will automatically open your default browser at:  
**http://localhost:8501**

---

## 5-Minute Live Viva Demonstration Script

Follow this step-by-step walkthrough during your examination:

1. **Step 1: Introduction (30 seconds)**
   - Introduce yourself: *"Good morning/afternoon Professors. Today I am presenting my Big Data Analytics mini-project: The Social Media Analytics Dashboard."*
   - Mention the core problem: *"Social media data is typically scattered across platforms with inconsistent column names and missing values. Our platform provides automated schema discovery, rigorous data profiling, statistical analytics, offline NLP, and unsupervised machine learning."*

2. **Step 2: Instant Demonstration (60 seconds)**
   - In the sidebar, click the **"Load Pre-Generated Sample Data (700 Posts)"** button.
   - Point out that 700 multi-platform posts (Twitter/X, Instagram, LinkedIn, YouTube, Facebook) spanning 12 months are instantly ingested and analyzed in under 0.5 seconds.
   - Show the **Dashboard Overview**:
     - Metric cards: Total Posts (700), Total Engagement (~191K), Avg Engagement per post (~273), and Engagement Rate.
     - Platform breakdown bar chart showing YouTube and LinkedIn leading engagement.
     - The "Highest Engaging Post Overall" callout card.

3. **Step 3: Column Mapping & Cleaning Audit (60 seconds)**
   - Click **"Dataset Upload & Quality"** in the sidebar.
   - Show the **Column Synonym Mapping** table: explain that whether an uploaded CSV names a column `impressions`, `views`, or `reach`, the regex heuristics map it automatically.
   - Show the **Data Quality Health Index** and the **Data Cleaning Audit Trail**, proving that no rows or values are modified without an explicit audit log.

4. **Step 4: Machine Learning Clustering (60 seconds)**
   - Click **"Machine Learning (K-Means)"** in the sidebar.
   - Explain why clustering is needed: *"Social posts do not have predefined category labels. Unsupervised K-Means groups content by engagement patterns."*
   - Point out the **StandardScaler**: *"We normalize metrics to zero-mean unit-variance so large numbers like Impressions don't dwarf Comments."*
   - Adjust the cluster slider from `k=3` to `k=4` and click **"Retrain Model"** to show real-time machine learning execution.
   - Show the **2D PCA projection scatter plot** and the **Cluster Archetype cards**.

5. **Step 5: SQLite Database & Deliverables Export (60 seconds)**
   - Click **"Analysis History (SQLite)"** to show that every run, timestamp, and result snapshot is stored in the relational SQLite database.
   - Click **"Report & Presentation Export"** to demonstrate:
     - Downloading the Cleaned CSV.
     - Downloading the Full Results JSON.
     - Downloading the 12-slide PowerPoint Presentation (`.pptx`).

---

## Viva Examination: Top 10 Questions & Answers

### Q1: What makes this a Big Data Analytics (BDA) project rather than basic data analysis?
**Answer:** The project implements the foundational architectural patterns of Big Data Engineering:
1. Automated ETL and schema harmonization for heterogeneous inputs.
2. In-memory vectorized processing capable of scaling across large batches.
3. Decoupled relational persistence (storing file references and aggregated analytical models in SQLite while avoiding database bloat).
4. Addressing the 4 V's (Volume, Velocity, Variety, Veracity) through automated quality scoring and audit tracking.

### Q2: Why did you choose K-Means Clustering and how does it work?
**Answer:** In social media analytics, content performance lacks supervised ground-truth labels. K-Means is an unsupervised partitioning algorithm that clusters $N$ posts into $K$ distinct performance tiers by minimizing within-cluster variance (inertia):
$$\text{Inertia} = \sum_{i=0}^{n}\min_{\mu_j \in C}(||x_i - \mu_j||^2)$$
It iteratively updates $K$ centroids until Euclidean convergence.

### Q3: Why is `StandardScaler` mandatory before running K-Means?
**Answer:** K-Means relies on Euclidean distance:
$$d(p, q) = \sqrt{\sum_{i=1}^{n}(p_i - q_i)^2}$$
If one metric (e.g., Impressions) has values in the thousands and another (e.g., Comments) has values from 0 to 50, the distance calculation will be 99% dominated by impressions. `StandardScaler` standardizes each feature to $\mu = 0$ and $\sigma = 1$:
$$z = \frac{x - \mu}{\sigma}$$
ensuring equal weight across all engagement dimensions.

### Q4: Why use PCA (Principal Component Analysis) for visualization?
**Answer:** Our clustering uses 4 numerical dimensions (likes, comments, shares, impressions). Humans cannot visualize high-dimensional data directly. PCA computes eigenvectors of the covariance matrix to project the data onto the 2 orthogonal directions of maximum variance, enabling an intuitive 2D scatter plot.

### Q5: How is the Engagement Rate calculated and what are its assumptions?
**Answer:** The Engagement Rate is calculated as:
$$\text{Engagement Rate (\%)} = \left(\frac{\text{Total Likes} + \text{Total Comments} + \text{Total Shares}}{\text{Total Impressions}}\right) \times 100$$
**Assumption:** The dataset must contain an impression/view count representing the denominator (reach). If impressions are unavailable, the dashboard explicitly disallows the rate and explains why.

### Q6: How does the offline Sentiment Analysis function without heavy APIs?
**Answer:** To guarantee reliable offline operation without requiring paid cloud APIs or multi-gigabyte models, we engineered a rule-based linguistic polarity lexicon. It tokenizes text, handles negation flips (e.g., *"not good"*), computes positive vs. negative valence, and normalizes scores to $[-1.0, +1.0]$ via hyperbolic tangent scaling. We clearly label it in the UI as an estimated heuristic.

### Q7: Why store metadata and summaries in SQLite instead of raw post rows?
**Answer:** Inserting millions of raw social events into SQLite creates database locks, large file footprints, and slow bulk queries. In modern BDA design (e.g., Lakehouse / Metadata Catalog pattern), raw files remain in object/file storage while SQLite stores operational metadata, schema mappings, execution timestamps, and summary JSON snapshots.

### Q8: How does the column detection algorithm work?
**Answer:** `detect_columns` utilizes a dictionary of synonyms for standard social metrics. Column names in the uploaded CSV are stripped of non-alphanumeric characters, converted to lowercase, and matched against synonym pools using exact match priority followed by bounded substring matching.

### Q9: What happens if a dataset has missing columns or corrupt rows?
**Answer:** The application is built with defensive programming:
- Missing numerical values are imputed via median values or dropped based on user configuration.
- Corrupted dates are parsed with `format="mixed"` and coerced to `NaT`.
- Missing columns disable only dependent features (e.g., sentiment without text) while keeping all other modules fully functional, with clear UI indicators explaining what is omitted.

### Q10: What are the primary limitations and future industry scaling steps?
**Answer:**
- **Current Limitation:** Single-node memory execution limits dataset scale to several million rows.
- **Future Roadmap:**
  1. Horizontal scaling using Apache Spark / PySpark for distributed cluster execution.
  2. Live stream ingestion using Apache Kafka and Spark Streaming.
  3. Pre-trained transformer models (e.g., RoBERTa) for multilingual sentiment analysis.
  4. Direct OAuth2 API connectors for Meta Graph API, YouTube Data API, and X API v2.

---

## Testing Verification Report

The project has been tested with `test_suite.py` against 7 rigorous conditions:
- [PASS] **Test 1:** 700-post realistic sample dataset.
- [PASS] **Test 2:** Alternative column synonyms (`favs`, `replies`, `reposts`, `reach`, `network`, `content`).
- [PASS] **Test 3:** Dirty dataset with duplicate rows and missing cells.
- [PASS] **Test 4:** Text-only dataset without numerical engagement columns.
- [PASS] **Test 5:** Metrics-only dataset without text captions.
- [PASS] **Test 6:** Empty DataFrame inputs.
- [PASS] **Test 7:** SQLite database relational persistence and history retrieval.

**Overall Test Suite Result: 100% Passed (7/7)**

---

## License & Academic Attribution
Developed as an academic mini-project for **Big Data Analytics (BDA)** coursework in Computer Science & Engineering (AI & Data Science).  
Designed for educational and viva demonstration purposes.
