import gradio as gr
import pandas as pd
from rapidfuzz import fuzz
import os


def compare_company_domain(company: str, domain: str):
    """Compare company name to domain with fuzzy match"""
    if not company or not domain:
        return "Missing input", 0

    company_clean = company.lower().replace(" ", "")
    domain_clean = domain.lower().split(".")[0]

    score = fuzz.partial_ratio(company_clean, domain_clean)
    if score > 90:
        result = "Strong Match"
    elif score > 70:
        result = "Possible Match"
    else:
        result = "Low Match"

    return result, score


def process_file(file):
    df = pd.read_excel(file.name) if file.name.endswith(".xlsx") else pd.read_csv(file.name)
    if "Company" not in df.columns or "Domain" not in df.columns:
        return "❌ Your file must contain columns 'Company' and 'Domain'"

    output = []
    for _, row in df.iterrows():
        res, score = compare_company_domain(row["Company"], row["Domain"])
        output.append((row["Company"], row["Domain"], res, score))

    result_df = pd.DataFrame(output, columns=["Company", "Domain", "Result", "Score"])
    return result_df


# ----
