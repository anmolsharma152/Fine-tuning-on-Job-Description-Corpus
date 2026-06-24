#!/usr/bin/env bash
set -euo pipefail

# run_pipeline.sh
# End-to-end: generate dataset → split → (ready for Colab training)

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Indic Instructor Pipeline ==="

# Step 1: Generate
echo ""
echo "[1/3] Generating 15K instruction records..."
python data/generate_instructions.py --count 15000 --output data/raw_instructions.jsonl

# Step 2: Split
echo ""
echo "[2/3] Splitting into train/val..."
python data/split.py --input data/raw_instructions.jsonl

# Step 3: Summary
echo ""
echo "[3/3] Dataset ready:"
echo "  data/train.jsonl"
echo "  data/val.jsonl"
echo ""
echo "Next: Push to GitHub, then run on Colab:"
echo "  !bash setup/colab_setup.sh"
echo "  !python training/train.py"
