# [H] Integer overflows in Tensorflow

## Summary
Severity: High
Advisory: GHSA-rrx2-r989-2c43
CVE: CVE-2022-23567
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-rrx2-r989-2c43
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact 
The [implementations of `Sparse*Cwise*` ops](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/sparse_dense_binary_op_shared.cc) are vulnerable to integer overflows. These can be used to trigger large allocations (so, OOM based denial of service) or `CHECK`-fails when building new `TensorShape` objects (so, assert failures based denial of service):

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.SparseDenseCwiseDiv(
    sp_indices=np.array([[9]]),
    sp_values=np.array([5]),
    sp_shape=np.array([92233720368., 92233720368]),
    dense=np.array([4]))
```

We are missing some validation on the shapes of the input tensors as well as directly constructing a large `TensorShape` with user-provided dimensions. The latter is an instance of [TFSA-2021-198](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md) (CVE-2021-41197) and is easily fixed by replacing a call to `TensorShape` constructor with a call to `BuildTensorShape` static helper factory.

### Patches
We have patched the issue in GitHub commits [1b54cadd19391b60b6fcccd8d076426f7221d5e8](https://github.com/tensorflow/tensorflow/commit/1b54cadd19391b60b6fcccd8d076426f7221d5e8) and [e952a89b7026b98fe8cbe626514a93ed68b7c510](https://github.com/tensorflow/tensorflow/commit/e952a89b7026b98fe8cbe626514a93ed68b7c510).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rrx2-r989-2c43
- https://nvd.nist.gov/vuln/detail/CVE-2022-23567
- https://github.com/tensorflow/tensorflow/commit/1b54cadd19391b60b6fcccd8d076426f7221d5e8
- https://github.com/tensorflow/tensorflow/commit/e952a89b7026b98fe8cbe626514a93ed68b7c510
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-76.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-131.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/sparse_dense_binary_op_shared.cc
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md
