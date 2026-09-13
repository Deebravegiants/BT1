# [M] `CHECK` fail via inputs in `SparseFillEmptyRowsGrad`

## Summary
Severity: Medium
Advisory: GHSA-hq7g-wwwp-q46h
CVE: CVE-2022-41898
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-hq7g-wwwp-q46h
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
If [`SparseFillEmptyRowsGrad`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/sparse_fill_empty_rows_op_gpu.cu.cc) is given empty inputs, TensorFlow will crash.

```python
import tensorflow as tf
tf.raw_ops.SparseFillEmptyRowsGrad(
    reverse_index_map=[], grad_values=[], name=None
)
```

### Patches
We have patched the issue in GitHub commit [af4a6a3c8b95022c351edae94560acc61253a1b8](https://github.com/tensorflow/tensorflow/commit/af4a6a3c8b95022c351edae94560acc61253a1b8).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jiawei Liu, PhD student at University of Illinois, Urbana-Champaign.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hq7g-wwwp-q46h
- https://nvd.nist.gov/vuln/detail/CVE-2022-41898
- https://github.com/tensorflow/tensorflow/commit/af4a6a3c8b95022c351edae94560acc61253a1b8
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/sparse_fill_empty_rows_op_gpu.cu.cc
