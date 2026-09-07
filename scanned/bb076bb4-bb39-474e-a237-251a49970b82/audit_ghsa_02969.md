# [H] Undefined behavior via `nullptr` reference binding in sparse matrix multiplication

## Summary
Severity: High
Advisory: GHSA-4f99-p9c2-3j8x
CVE: CVE-2021-41219
CWE: CWE-125, CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-4f99-p9c2-3j8x
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
The [code for sparse matrix multiplication](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/sparse_matmul_op.cc#L954-L1086) is vulnerable to undefined behavior via binding a reference to `nullptr`:

```python
import tensorflow as tf
  
tf.raw_ops.SparseMatMul(
  a=[[1.0,1.0,1.0]],
  b=[[],[],[]],
  transpose_a=False,
  transpose_b=False,
  a_is_sparse=False, 
  b_is_sparse=True)
```

This occurs whenever the dimensions of `a` or `b` are 0 or less. In the case on one of these is 0, an empty output tensor should be allocated (to conserve the invariant that output tensors are always allocated when the operation is successful) but nothing should be written to it (that is, we should return early from the kernel implementation). Otherwise, attempts to write to this empty tensor would result in heap OOB access.

### Patches
We have patched the issue in GitHub commit [e6cf28c72ba2eb949ca950d834dd6d66bb01cfae](https://github.com/tensorflow/tensorflow/commit/e6cf28c72ba2eb949ca950d834dd6d66bb01cfae).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4f99-p9c2-3j8x
- https://nvd.nist.gov/vuln/detail/CVE-2021-41219
- https://github.com/tensorflow/tensorflow/commit/e6cf28c72ba2eb949ca950d834dd6d66bb01cfae
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-628.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-826.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-411.yaml
- https://github.com/tensorflow/tensorflow
