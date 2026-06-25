#!/usr/bin/env python3
"""
generate_test_sarvam_m.py
TEST — Sarvam-M 24B vs Nemotron-Super 49B throughput & quality comparison.

Sarvam-M is the bigger sibling of Sarvam-1 (our target model), specifically
trained for Indian languages. This tests if it's a good teacher.

Default model: sarvamai/sarvam-m
Default output: data/test_sarvam_m.jsonl

Usage:
    python data/generate_test_sarvam_m.py --count 50 --workers 10
"""

import os
import json
import argparse
import time
import concurrent.futures
from openai import OpenAI

_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

SEED_TASKS = {
    "translation": {"prompt": "Generate a {lang} instruction asking to translate text {from_lang} to {to_lang}, then provide the correct translation.", "count": 0},
    "summarization": {"prompt": "Generate a {lang} instruction asking to summarize a paragraph, then provide a summary.", "count": 0},
    "qa": {"prompt": "Generate a {lang} question-answer pair about {topic}.", "count": 0},
    "brainstorming": {"prompt": "Generate a {lang} instruction asking for ideas about {topic}, then provide 3-5 ideas.", "count": 0},
    "classification": {"prompt": "Generate a {lang} instruction asking to classify something, then provide the classification.", "count": 0},
    "creative": {"prompt": "Generate a {lang} creative writing instruction, then provide a short story or poem.", "count": 0},
    "grammar": {"prompt": "Generate a {lang} instruction asking to correct grammar in a sentence, then provide the corrected version.", "count": 0},
}

def build_client():
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not set.")
    return OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)

def fetch_single_record(client, model, seed, temperature):
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a dataset generator. Generate one instruction-output pair in the specified language and script. Output ONLY valid JSON with keys 'instruction' and 'output'. The 'output' value MUST be a plain string (text only), not a JSON object or array. Use Hinglish (Hindi+English mix in Roman script), Hindi (Devanagari), or English as requested."},
                {"role": "user", "content": seed},
            ],
            temperature=temperature,
            max_tokens=512,
        )
        text = resp.choices[0].message.content.strip()
        record = try_parse_json(text)
        if record and "instruction" in record and "output" in record:
            return record
        print(f"  [warn] Failed to parse: {text[:80]}...")
        return None
    except Exception as e:
        print(f"  [error] {e}")
        time.sleep(2)
        return None

def generate_batch(client, model, seed_prompts, temperature=0.8, workers=10):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(fetch_single_record, client, model, seed, temperature): seed for seed in seed_prompts}
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            if record:
                results.append(record)
    return results

def try_parse_json(text):
    import re
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None

def build_seed_prompts(count, languages, scripts):
    topics = ["machine learning", "artificial intelligence", "cloud computing", "climate change", "Indian economy", "cricket", "Bollywood", "Indian festivals", "technology", "education", "healthcare in India", "startups", "remote work", "data science"]
    combos = [(l, s) for l in languages for s in scripts if not (l == "hi" and s == "roman")]
    prompts, task_types = [], list(SEED_TASKS.keys())
    for i in range(count):
        lang, script = combos[i % len(combos)]
        task = task_types[i % len(task_types)]
        topic = topics[i % len(topics)]
        lang_label = {"hi": "Hindi (Devanagari)", "en": "English", "hinglish": "Hinglish (Roman)"}.get(lang, lang)
        prompts.append(f"Generate a {lang_label} instruction-output pair. Task type: {task}. Topic: {topic}. Make the instruction realistic and natural. The 'output' field must be a plain text string (NOT a JSON object or list). Output as JSON with keys 'instruction' and 'output'.")
    return prompts

def main():
    parser = argparse.ArgumentParser(description="[TEST] Generate instruction data via Sarvam-M 24B")
    parser.add_argument("--count", default=50, type=int, help="Records to generate")
    parser.add_argument("--output", default="data/test_sarvam_m.jsonl", help="Output JSONL path")
    parser.add_argument("--languages", nargs="+", default=["hinglish", "hi", "en"], choices=["hinglish", "hi", "en"])
    parser.add_argument("--scripts", nargs="+", default=["roman", "devanagari"], choices=["roman", "devanagari"])
    parser.add_argument("--model", default="sarvamai/sarvam-m", help="NVIDIA NIM model ID")
    parser.add_argument("--batch_size", default=10, type=int)
    parser.add_argument("--temperature", default=0.8, type=float)
    parser.add_argument("--workers", default=10, type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    existing_count = 0
    if args.resume and os.path.exists(args.output):
        with open(args.output) as f:
            existing_count = sum(1 for _ in f)
        if existing_count >= args.count:
            print(f"Already have {existing_count}/{args.count}. Nothing to do.")
            return
        print(f"Resuming: {existing_count} exist, generating {args.count - existing_count} more")

    client = build_client()
    seed_prompts = build_seed_prompts(args.count, args.languages, args.scripts)
    if existing_count > 0:
        seed_prompts = seed_prompts[existing_count:]

    print(f"[TEST] Model: {args.model}")
    print(f"[TEST] Generating up to {args.count} (batch={args.batch_size}, workers={args.workers})...")
    start = time.time()
    all_records = []
    with open(args.output, "a") as f:
        for i in range(0, len(seed_prompts), args.batch_size):
            batch = seed_prompts[i:i+args.batch_size]
            records = generate_batch(client, args.model, batch, args.temperature, args.workers)
            for rec in records:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
            all_records.extend(records)
            print(f"  Progress: {existing_count + len(all_records)}/{args.count}")
            if existing_count + len(all_records) >= args.count:
                break

    elapsed = time.time() - start
    total = existing_count + len(all_records)
    rps = len(all_records) / elapsed if elapsed else 0
    print(f"\nDone! {total} records in {elapsed:.1f}s ({rps:.2f} rec/s)")

    lang_counts = {}
    for rec in all_records:
        inst = rec.get("instruction", "")
        if any("\u0900" <= c <= "\u097F" for c in inst):
            tag = "hindi"
        elif any(c in inst for c in "ko hai se mein ka ki"):
            tag = "hinglish"
        else:
            tag = "english"
        lang_counts[tag] = lang_counts.get(tag, 0) + 1
    print(f"Language breakdown: {lang_counts}")

if __name__ == "__main__":
    main()
