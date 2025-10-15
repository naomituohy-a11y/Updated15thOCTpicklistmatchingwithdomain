import gradio as gr
import pandas as pd
from rapidfuzz import fuzz, process


# -------------------------------
# 🔹 Helper functions
# -------------------------------

def clean_text(text):
    """Basic text cleaning for matching"""
    if pd.isna(text):
        return ""
    return str(text).strip().lower()


def fuzzy_match(company_name, reference_list, threshold=85):
    """Perform fuzzy matching against a reference list"""
    if not company_name or not reference_list:
        return ""
    match, score, _ = process.extractOne(company_name, reference_list, scorer=fuzz.token_sort_ratio)
    return match if score >= threshold else ""


def process_files(tal_file, master_file, tal_column, master_column, threshold):
    """Process TAL vs Master to find matches"""
    try:
        # Load files
        tal_df = pd.read_excel(tal_file) if tal_file.name.endswith(".xlsx") else pd.read_csv(tal_file)
        master_df = pd.read_excel(master_file) if master_file.name.endswith(".xlsx") else pd.read_csv(master_file)

        # Clean data
        tal_df[tal_column] = tal_df[tal_column].apply(clean_text)
        master_df[master_column] = master_df[master_column].apply(clean_text)

        # Prepare master list
        master_names = master_df[master_column].dropna().unique().tolist()

        # Perform matching
        matches = [fuzzy_match(name, master_names, threshold) for name in tal_df[tal_column]]
        tal_df["Matched Company"] = matches

        # Merge preview
        merged_df = pd.merge(
            tal_df,
            master_df,
            left_on="Matched Company",
            right_on=master_column,
            how="left",
            suffixes=("_TAL", "_MASTER")
        )

        return merged_df.head(50)
    except Exception as e:
        return f"❌ Error: {str(e)}"


# -------------------------------
# 🔹 Gradio UI
# -------------------------------

with gr.Blocks(title="TAL vs Master Fuzzy Matcher") as demo:
    gr.Markdown("## 🔍 TAL vs Master Matching Tool")
    gr.Markdown("Upload your TAL and Master files to find company name matches using fuzzy logic.")

    with gr.Row():
        tal_file = gr.File(label="📄 Upload TAL File (.csv or .xlsx)")
        master_file = gr.File(label="📄 Upload Master File (.csv or .xlsx)")

    with gr.Row():
        tal_column = gr.Textbox(label="TAL Column Name", placeholder="Company")
        master_column = gr.Textbox(label="Master Column Name", placeholder="Company Name")
        threshold = gr.Slider(70, 100, value=85, step=1, label="Fuzzy Match Threshold (%)")

    run_button = gr.Button("🚀 Run Matching")
    output = gr.Dataframe(label="Matched Results (Preview)", interactive=False)

    run_button.click(
        fn=process_files,
        inputs=[tal_file, master_file, tal_column, master_column, threshold],
        outputs=output
    )

    gr.Markdown("---")
    gr.Markdown("✅ Built for TAL ↔ Master data alignment")


# -------------------------------
# 🔹 Correct Railway launch
# -------------------------------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))

    # Important: queue() + prevent_thread_lock keeps process alive
    demo.queue(concurrency_count=3)
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_api=False,
        quiet=False,
        prevent_thread_lock=True
    )
