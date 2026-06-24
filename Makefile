.PHONY: generate split train train-dry train-colab eval eval-dry serve clean all

# ─── Dataset ────────────────────────────────────────────────────────────────

generate:
	python data/generate_instructions.py --count 15000 --output data/raw_instructions.jsonl

split:
	python data/split.py --input data/raw_instructions.jsonl

# ─── Training ────────────────────────────────────────────────────────────────

train:
	python training/train.py

train-dry:
	python training/train.py --dry-run

train-colab:
	python training/train.py --model_id sarvamai/sarvam-1 \
		--train_file data/train.jsonl \
		--val_file data/val.jsonl \
		--epochs 3 --batch_size 4

# ─── Evaluation ──────────────────────────────────────────────────────────────

eval:
	python eval/benchmark.py --model sarvamai/sarvam-1 --adapter models/sarvam-1-indic-instructor --test_file data/val.jsonl --num_samples 500

eval-dry:
	python eval/benchmark.py --dry-run --num_samples 5

# ─── Serving ─────────────────────────────────────────────────────────────────

serve:
	cd serving && python app.py --model sarvamai/sarvam-1 --host 127.0.0.1 --port 8000

# ─── Utility ─────────────────────────────────────────────────────────────────

clean:
	rm -rf data/raw_instructions.jsonl data/train.jsonl data/val.jsonl
	rm -rf models/
	rm -rf eval/results.json
	rm -rf logs/
	rm -rf wandb/
	rm -rf __pycache__ */__pycache__ */*/__pycache__

# ─── Pipeline ────────────────────────────────────────────────────────────────

all: generate split
	@echo "Pipeline complete. Run 'make train-colab' on Colab."
