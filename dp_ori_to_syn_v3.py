#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
import json
import threading
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
from tqdm.auto import tqdm

# ─── 配置 ────────────────────────────────────────────────────────────────
MODEL_PATH = "/home/sjie/llama_models/merged-llama3.1-8b-dp-fp16"
INPUT_CSV = "ori_214000_fix.csv"
OUTPUT_CSV = "ori_214000_fix_dp_v3.csv"
BATCH_SIZE = 100
TOTAL_ROWS = 214000

HEADER = "id,age,education,occupation,income,mobility,health,life_quality"
NUMERIC = ["age", "income", "mobility", "health", "life_quality"]
BOUNDS = {
    "age": (18, 90),
    "income": (15000, 200000),
    "mobility": (0, 1),
    "health": (1, 5),
    "life_quality": (1, 10),
}
EPSILON = 0.5
MEAN_TRIES = 5

# ─── 載入資料 ──────────────────────────────────────────────────────────────
raw_csv = Path(INPUT_CSV).read_text(encoding="utf-8").strip()
assert raw_csv.splitlines()[0].strip() == HEADER, "CSV header mismatch"
orig_df = pd.read_csv(io.StringIO(raw_csv), dtype={col: float for col in NUMERIC})

# ─── 載入模型 ──────────────────────────────────────────────────────────────
tok = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True,
    max_memory={0: "23GiB", "cpu": "30GiB"},
)

def memory_optimized_chat(prompt: str) -> str:
    with torch.inference_mode():
        inputs = tok(prompt, return_tensors="pt").to(model.device)
        streamer = TextIteratorStreamer(tok, skip_special_tokens=True)
        generation_args = dict(
            **inputs,
            max_new_tokens=400,
            temperature=0.9,
            top_p=0.9,
            streamer=streamer,
            eos_token_id=tok.eos_token_id,
            use_cache=True,
            pad_token_id=tok.eos_token_id,
            do_sample=True,
        )
        thread = threading.Thread(target=model.generate, kwargs=generation_args)
        thread.start()
        output = []
        for token in streamer:
            output.append(token)
            if len(output) % 10 == 0:
                torch.cuda.empty_cache()
        thread.join()
        return "".join(output).strip()

def safe_json_parse(text):
    try:
        return json.loads(text)
    except Exception:
        try:
            fixed = re.sub(r"'", '"', text)
            return json.loads(fixed)
        except Exception:
            return None

def process_noisy_means(noisy_means):
    processed = {}
    processed['age'] = int(np.clip(round(noisy_means['age']), *BOUNDS['age']))
    processed['income'] = int(np.clip(round(noisy_means['income']), *BOUNDS['income']))
    processed['mobility'] = round(np.clip(noisy_means['mobility'], *BOUNDS['mobility']), 3)
    processed['health'] = int(np.clip(round(noisy_means['health']), *BOUNDS['health']))
    processed['life_quality'] = int(np.clip(round(noisy_means['life_quality']), *BOUNDS['life_quality']))
    return processed

def validate_means(candidate: dict) -> bool:
    processed = process_noisy_means(candidate)
    demo = {'age': 53.217, 'income': 68954.428, 'mobility': 0.587, 'health': 3.220, 'life_quality': 6.787}
    demo_diff = sum(abs(processed[k] - demo[k]) for k in NUMERIC)
    return demo_diff > 0.05

# ─── Phase 1: 讓 LLaMA 產生帶噪均值 ─────────────────────────────
orig_means = {col: orig_df[col].mean() for col in NUMERIC}
PH1 = f"""
You are a differential privacy assistant.

Given the original means for numeric columns:
{orig_means}

And their bounds:
{BOUNDS}

Add ε=0.5 Laplace noise to each mean (clip to bounds after adding noise).

Return ONLY a JSON with 3-decimal values, e.g.:
{{"age": 51.234, "income": 70000.123, "mobility": 0.543, "health": 3.456, "life_quality": 7.890}}

Do NOT include any other text or code.
"""

means = None
for attempt in range(1, MEAN_TRIES + 1):
    print(f"Phase-1 attempt {attempt}/{MEAN_TRIES}")
    response = memory_optimized_chat(PH1)
    print(f"Model response:\n{response}\n")

    match = re.search(r"\{.*?\}", response, re.DOTALL)
    if not match:
        print("No JSON found, retrying...")
        continue

    parsed = safe_json_parse(match.group())
    if not parsed:
        print("JSON parse failed, retrying...")
        continue

    try:
        candidate = {k: float(v) for k, v in parsed.items()}
    except Exception as e:
        print(f"Value conversion error: {e}, retrying...")
        continue

    if validate_means(candidate):
        means = process_noisy_means(candidate)
        print(f"Validated DP means: {means}")
        break
    else:
        print("DP means too close to demo values, retrying...")

if not means:
    warnings.warn("Model failed to produce valid DP means, using fallback")
    means = {}
    for col in NUMERIC:
        noise = np.random.laplace(loc=orig_means[col], scale=(BOUNDS[col][1] - BOUNDS[col][0]) / EPSILON)
        noisy = np.clip(noise, *BOUNDS[col])
        means[col] = process_noisy_means({col: noisy})[col]
    print(f"Fallback DP means: {means}")

# ─── Phase 2: 對每筆資料獨立加噪 ─────────────────────────────
scale_dict = {col: (BOUNDS[col][1] - BOUNDS[col][0]) / EPSILON for col in NUMERIC}

pbar = tqdm(total=TOTAL_ROWS // BATCH_SIZE, desc="Generating DP CSV batches")
all_rows = []

for batch_start in range(0, TOTAL_ROWS, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, TOTAL_ROWS)
    batch_df = orig_df.iloc[batch_start:batch_end].copy()

    # 對每筆資料的每個數值欄位獨立加拉普拉斯噪聲並裁剪
    for col in NUMERIC:
        noise = np.random.laplace(loc=0, scale=scale_dict[col], size=len(batch_df))
        noisy_vals = batch_df[col] + noise
        clipped = np.clip(noisy_vals, BOUNDS[col][0], BOUNDS[col][1])
        if col == "mobility":
            batch_df[col] = np.round(clipped, 3)
        else:
            batch_df[col] = np.round(clipped).astype(int)

    csv_str = batch_df.to_csv(index=False, header=(batch_start == 0), lineterminator="\n").strip()
    if batch_start == 0:
        all_rows.append(csv_str)
    else:
        all_rows.append("\n".join(csv_str.splitlines()[1:]))

    pbar.update(1)

pbar.close()

final_csv = "\n".join(all_rows)
Path(OUTPUT_CSV).write_text(final_csv, encoding="utf-8")
print(f"DP protected CSV saved to: {OUTPUT_CSV}")
