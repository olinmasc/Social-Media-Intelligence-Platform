"""
generate_sample_data.py - Synthetic Social Media Dataset Generator
Generates a realistic, reproducible dataset of 700+ social media posts across 5 platforms
spanning 12 months with authentic engagement distributions, realistic captions, and hashtags.
Designed for Big Data Analytics (BDA) mini-project demonstration.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_social_media_dataset(num_posts: int = 700, output_path: str = "data/sample_social_media.csv") -> pd.DataFrame:
    """
    Generates realistic social media post data with log-normal engagement distributions,
    authentic multi-platform themes, sentiment, and hashtags.
    """
    np.random.seed(42)
    random.seed(42)
    
    platforms = ["Twitter/X", "Instagram", "LinkedIn", "YouTube", "Facebook"]
    platform_probs = [0.28, 0.26, 0.22, 0.12, 0.12]
    
    # Topic templates per platform (pure clean text, no emojis)
    templates = {
        "Twitter/X": [
            ("Excited to share our latest breakthrough in Big Data Analytics! Real-time stream processing is the future. {tag}", ["#BigData", "#DataScience", "#Analytics", "#AI", "#TechNews"]),
            ("10 Python libraries every Data Scientist must master in 2024. A thread: {tag}", ["#Python", "#MachineLearning", "#DataScience", "#Coding", "#TechTips"]),
            ("Unpopular opinion: SQL is still the single most important skill for any data analytics engineer. Agree or disagree? {tag}", ["#SQL", "#Database", "#DataEngineering", "#CareerAdvice"]),
            ("Deploying our ML pipeline to production today! Latency dropped by 45% using optimized vector operations. {tag}", ["#MachineLearning", "#DevOps", "#CloudComputing", "#AI"]),
            ("Just released our open-source interactive dashboard built with Streamlit and Plotly! Link below. {tag}", ["#OpenSource", "#Streamlit", "#Python", "#DataViz"]),
            ("Data quality issues can ruin even the most sophisticated neural network. Always validate your inputs first. {tag}", ["#DataQuality", "#MachineLearning", "#CleanData", "#AI"]),
            ("Cloud costs were out of control until we optimized our data aggregation queries. Saved $12k/month! {tag}", ["#CloudCost", "#DataOps", "#FinOps", "#AWS"]),
            ("Debugging distributed systems at 2 AM hits different. Found a race condition in the message queue! {tag}", ["#SoftwareEngineering", "#CodingLife", "#Tech"]),
            ("Why synthetic data generation is becoming crucial for privacy-preserving AI development. {tag}", ["#AI", "#SyntheticData", "#Privacy", "#Ethics"]),
            ("Great discussion on BDA frameworks and scalability at the regional tech summit today. {tag}", ["#BDA", "#Conference", "#Innovation", "#TechSummit"])
        ],
        "Instagram": [
            ("A day in the life of a Data Science student! Coffee, algorithms, and visualization dashboards. View my desk setup: {tag}", ["#DeskSetup", "#DataScientist", "#CodingLife", "#StudentLife", "#TechVibes"]),
            ("Behind the scenes of our college BDA project! Building interactive dashboards that bring data to life. {tag}", ["#DataViz", "#ProjectShowcase", "#StudentEngineer", "#AI", "#Python"]),
            ("Transforming raw, messy spreadsheets into stunning visual insights! Which chart style is your favorite? {tag}", ["#DataVisualization", "#Plotly", "#Analytics", "#UIUX", "#Design"]),
            ("Late night study sessions powered by caffeine and determination. Final year project progress! {tag}", ["#StudyGram", "#TechStudent", "#FinalYear", "#CodingJourney"]),
            ("From raw CSV files to predictive machine learning clusters in under 5 minutes. The power of modern analytics! {tag}", ["#MachineLearning", "#DataScience", "#PythonCode", "#TechTrends"]),
            ("Celebrating our mini-project milestone! Hard work, teamwork, and lots of debugging paid off. {tag}", ["#Milestone", "#Engineering", "#CampusLife", "#Teamwork"]),
            ("Design matters in data analytics. Clean dark mode dashboards make complex numbers easy to understand. {tag}", ["#UIUX", "#DashboardDesign", "#TechAesthetics", "#Frontend"])
        ],
        "LinkedIn": [
            ("I am thrilled to announce the completion of our Big Data Analytics Mini-Project: 'Social Media Analytics Dashboard'. Here are 3 key architectural insights from building an end-to-end analytics platform: {tag}", ["#BigDataAnalytics", "#DataScience", "#MachineLearning", "#CareerMilestone"]),
            ("Data is meaningless without contextual interpretation. In our recent social analytics study, we analyzed engagement patterns across platforms to identify peak ROI windows. {tag}", ["#Analytics", "#DigitalStrategy", "#DataDriven", "#MarketingAnalytics"]),
            ("Reflecting on the importance of robust data cleaning pipelines in modern BDA systems. Garbage in, garbage out remains the golden rule. {tag}", ["#DataQuality", "#DataEngineering", "#ETL", "#BestPractices"]),
            ("Honored to present our findings at the college symposium on AI and Data Science. Continuous learning and practical implementation drive genuine engineering growth. {tag}", ["#Conference", "#AI", "#ComputerScience", "#Innovation"]),
            ("How unsupervised machine learning (K-Means Clustering) helps segment high-performing content without labeled ground truth. Full case study: {tag}", ["#MachineLearning", "#KMeans", "#Clustering", "#DataMining"]),
            ("Key takeaways from transitioning our analytics backend to modular Python architectures with persistent SQLite caching. {tag}", ["#SoftwareEngineering", "#Architecture", "#Python", "#Performance"])
        ],
        "YouTube": [
            ("Full Tutorial: Building a Full-Stack Social Media Analytics Dashboard with Python & Streamlit from Scratch! {tag}", ["#Tutorial", "#Python", "#Streamlit", "#DataAnalytics", "#LearnToCode"]),
            ("How I analyzed 1,000,000 social media posts using Pandas, Plotly, and K-Means Clustering | Project Walkthrough {tag}", ["#ProjectWalkthrough", "#DataScience", "#MachineLearning", "#Coding"]),
            ("Streamlit vs Dash vs Gradio in 2024: Which Python framework is best for your Data Science Portfolio project? {tag}", ["#Streamlit", "#FrameworkComparison", "#TechReview", "#DataViz"]),
            ("Complete Big Data Analytics Viva Preparation Guide: 50 Questions & Answers for Engineering Students! {tag}", ["#VivaPreparation", "#EngineeringExam", "#BDA", "#StudentGuide"])
        ],
        "Facebook": [
            ("Our department's annual Techfest showcase was a huge success! Proud of our team for demonstrating the Social Media Analytics Dashboard. {tag}", ["#CampusEvent", "#Engineering", "#TechFest", "#StudentAchievements"]),
            ("Tips for engineering students preparing for semester project presentations: structure, confidence, and live demos! {tag}", ["#CollegeTips", "#EngineeringLife", "#Success", "#StudentCommunity"]),
            ("Alumni talk on industry expectations for Big Data Analytics and AI engineers was truly inspiring today. {tag}", ["#AlumniTalk", "#FutureReady", "#DataScienceCareers", "#CollegeNews"])
        ]
    }
    
    end_date = datetime(2024, 11, 1, 18, 30, 0)
    records = []
    
    for i in range(1, num_posts + 1):
        post_id = f"POST_{i:04d}"
        platform = np.random.choice(platforms, p=platform_probs)
        
        template_pair = random.choice(templates[platform])
        raw_text_template, tag_pool = template_pair
        
        num_tags = random.randint(1, min(3, len(tag_pool)))
        chosen_tags = random.sample(tag_pool, num_tags)
        tag_str = " ".join(chosen_tags)
        content_text = raw_text_template.format(tag=tag_str)
        
        days_ago = random.randint(0, 300)
        hour_weights = np.array([
            0.01, 0.01, 0.01, 0.01, 0.01, 0.02, # 00-05
            0.03, 0.05, 0.07, 0.08, 0.08, 0.07, # 06-11
            0.07, 0.06, 0.05, 0.06, 0.07, 0.08, # 12-17
            0.09, 0.08, 0.06, 0.04, 0.02, 0.01  # 18-23
        ])
        hour_probs = hour_weights / hour_weights.sum()
        hour = int(np.random.choice(range(24), p=hour_probs))
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        post_time = end_date - timedelta(days=days_ago, hours=(24 - hour), minutes=minute, seconds=second)
        date_str = post_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if platform == "YouTube":
            base_impressions = int(np.random.lognormal(mean=9.2, sigma=1.0))
        elif platform == "LinkedIn":
            base_impressions = int(np.random.lognormal(mean=7.5, sigma=0.85))
        elif platform == "Instagram":
            base_impressions = int(np.random.lognormal(mean=8.0, sigma=0.9))
        elif platform == "Twitter/X":
            base_impressions = int(np.random.lognormal(mean=7.2, sigma=1.1))
        else: # Facebook
            base_impressions = int(np.random.lognormal(mean=7.0, sigma=0.8))
        
        impressions = max(120, min(base_impressions, 180000))
        
        like_rate = np.random.uniform(0.025, 0.075)
        likes = max(1, int(impressions * like_rate + np.random.normal(0, 5)))
        
        comment_rate = np.random.uniform(0.04, 0.18)
        comments = max(0, int(likes * comment_rate + np.random.normal(0, 2)))
        
        share_rate = np.random.uniform(0.03, 0.16)
        shares = max(0, int(likes * share_rate + np.random.normal(0, 1)))
        
        if random.random() < 0.035:
            multiplier = random.uniform(2.5, 5.0)
            likes = int(likes * multiplier)
            comments = int(comments * multiplier)
            shares = int(shares * multiplier)
            impressions = int(impressions * multiplier)
            
        records.append({
            "post_id": post_id,
            "date": date_str,
            "platform": platform,
            "text": content_text,
            "hashtags": ", ".join(chosen_tags),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "impressions": impressions
        })
        
    df = pd.DataFrame(records)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} posts successfully saved to {output_path}")
    return df

if __name__ == "__main__":
    generate_social_media_dataset()
