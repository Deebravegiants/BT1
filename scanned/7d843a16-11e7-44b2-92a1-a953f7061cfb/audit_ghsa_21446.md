# [M] `CHECK_EQ` fail via input in `SparseMatrixNNZ`

## Summary
Severity: Medium
Advisory: GHSA-g9fm-r5mm-rf9f
CVE: CVE-2022-41901
CWE: CWE-20, CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-g9fm-r5mm-rf9f
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
An input `sparse_matrix` that is not a matrix with a shape with rank 0 will trigger a `CHECK` fail in [`tf.raw_ops.SparseMatrixNNZ`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/sparse/sparse_matrix.h).

```python
import tensorflow as tf
tf.raw_ops.SparseMatrixNNZ(sparse_matrix=[])
```

### Patches
We have patched the issue in GitHub commit [f856d02e5322821aad155dad9b3acab1e9f5d693](https://github.com/tensorflow/tensorflow/commit/f856d02e5322821aad155dad9b3acab1e9f5d693).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g9fm-r5mm-rf9f
- https://nvd.nist.gov/vuln/detail/CVE-2022-41901
- https://github.com/tensorflow/tensorflow/commit/f856d02e5322821aad155dad9b3acab1e9f5d693
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/sparse/sparse_matrix.h
