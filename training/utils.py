#!/usr/bin/env python3
"""
utils.py
Utilities for prompt formatting and preprocessing during training.
"""
from typing import List, Dict, Any

def format_chatml(messages: List[Dict[str, str]]) -> str:
    """
    Format a list of ChatML messages into a single text sequence.
    Example input:
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
    Example output:
        <|im_start|>system
        You are a helpful assistant.<|im_end|>
        <|im_start|>user
        Hello<|im_end|>
        <|im_start|>assistant
        Hi there!<|im_end|>
    """
    formatted = ""
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        formatted += f"<|im_start|>{role}\n{content}<|im_end|>\n"
    return formatted

def formatting_prompts_func(example: Dict[str, Any]) -> List[str]:
    """
    Formatting function for SFTTrainer. Receives examples from the dataset
    and returns a list of formatted ChatML text sequences.
    """
    # Handles both batched and single example inputs
    output_texts = []
    
    # Check if the example is a batch or single
    if isinstance(example.get("messages"), list) and len(example["messages"]) > 0:
        if isinstance(example["messages"][0], list):
            # Batch of conversations
            for messages in example["messages"]:
                output_texts.append(format_chatml(messages))
        else:
            # Single conversation
            output_texts.append(format_chatml(example["messages"]))
            
    return output_texts
