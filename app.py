import gradio as gr
import pandas as pd
from rapidfuzz import fuzz, process
import time

def match_domains(file1, file2, threshold):
    try:
        df1 = pd.read_excel(file1) if file1.name.endswith(".xlsx") else pd.read_csv(file1)
        df2 = pd.read_excel(file2) if file2.name.endswith(".xlsx") else pd.read_csv(file2)
    except Exception as e:
        return f"❌ Error reading files: {e}"

    col1 = df1.columns[0]
    col2 = df2.columns[0]
    matches = []

    for name in df1[col1].dropna().astype(str):
        best = process.extractOne(
            name, df2[col2].dropna().astype(str), scorer=fuzz.token_sort_ratio
        )
        if best and best[1] >= threshold:
            matches.append((name, best[0], best[1]))

    if not matches:
        return "No matches found."

    result_df = pd.DataFrame(matches, columns=["File1 Name", "Best Match", "Match %"])
    out_path = "/tmp/match_results.xlsx"
    result_df.to_excel(out_path, index=False)
    return out_path

with gr.Blocks(title="Domain/Company Matcher") as demo:
    gr.Markdown("### 🔍 Upload two files to compare domains or company names")

    file1 = gr.File(label="Upload First File")
    file2 = gr.File(label="Upload Second File")
    threshold = gr.Slider(0, 100, value=90, step=1, label="Match Threshold (%)")

    output = gr.File(label="Download Matched Results")
    run_btn = gr.Button("Run Matching")

    run_btn.click(
        fn=match_domains,
        inputs=[file1, file2, threshold],
        outputs=output,
        concurrency_limit=3
    )

demo.launch(server_name="0.0.0.0", server_port=8080, share=False)

# Keep the container alive
while True:
    print("✅ Health check: app is running")
    time.sleep(60)
