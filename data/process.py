#!/usr/bin/env python3
"""
process.py
Preprocesses the raw job descriptions, formats them using ChatML style
dialogs, and splits the data into train and validation sets.
"""
import os
import json
import argparse
import random
from typing import Dict, Any

def format_to_chatml(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a job record into prompt and completion columns.
    This structure is natively supported by TRL's completion-only loss.
    """
    system_prompt = "You are a professional HR assistant specializing in parsing and classifying Indian job postings."
    
    user_prompt = (
        f"Analyze the following job description. Classify it into a Role Category "
        f"(Software Engineering, Data Science, Product Management, Marketing, HR, Finance) "
        f"and determine its Salary Bucket (Entry, Mid, Senior, Executive).\n\n"
        f"Job Description:\n{job['job_description']}"
    )
    
    prompt = (
        f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
        f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    
    completion = (
        f"Role Category: {job['role_category']}\n"
        f"Salary Bucket: {job['salary_bucket']}<|im_end|>"
    )
    
    return {
        "prompt": prompt,
        "completion": completion
    }

def main():
    parser = argparse.ArgumentParser(description="Process and split job description dataset")
    parser.add_argument("--input", type=str, default="data/raw_jobs.jsonl", help="Path to raw jobs jsonl file")
    parser.add_argument("--train_output", type=str, default="data/train.jsonl", help="Path to save train split")
    parser.add_argument("--val_output", type=str, default="data/val.jsonl", help="Path to save validation split")
    parser.add_argument("--split_ratio", type=float, default=0.9, help="Percentage of data for training")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for split reproducibility")
    
    args = parser.parse_args()
    
    random.seed(args.seed)
    
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist. Run scraper.py first.")
        return
        
    print(f"Reading raw data from {args.input}...")
    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    print(f"Loaded {len(records)} raw records. Formatting to ChatML...")
    formatted_records = [format_to_chatml(rec) for rec in records]
    
    # Shuffle and split
    random.shuffle(formatted_records)
    split_idx = int(len(formatted_records) * args.split_ratio)
    
    train_data = formatted_records[:split_idx]
    val_data = formatted_records[split_idx:]
    
    # Ensure parent directory of outputs exists
    os.makedirs(os.path.dirname(args.train_output), exist_ok=True)
    os.makedirs(os.path.dirname(args.val_output), exist_ok=True)
    
    print(f"Saving {len(train_data)} training records to {args.train_output}...")
    with open(args.train_output, "w", encoding="utf-8") as f:
        for rec in train_data:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    print(f"Saving {len(val_data)} validation records to {args.val_output}...")
    with open(args.val_output, "w", encoding="utf-8") as f:
        for rec in val_data:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            
    print("Preprocessing and train/val split complete!")

if __name__ == "__main__":
    main()
