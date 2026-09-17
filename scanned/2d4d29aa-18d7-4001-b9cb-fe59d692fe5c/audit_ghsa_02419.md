# [H] Heap out of bounds access in sparse reduction operations

## Summary
Severity: High
Advisory: GHSA-cgfm-62j4-v4rf
CVE: CVE-2021-37635
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-cgfm-62j4-v4rf
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation of sparse reduction operations in TensorFlow can trigger accesses outside of bounds of heap allocated data:

```python
import tensorflow as tf

x = tf.SparseTensor(
      indices=[[773, 773, 773], [773, 773, 773]],
      values=[1, 1],
      dense_shape=[337, 337, 337])
tf.sparse.reduce_sum(x, 1)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/a1bc56203f21a5a4995311825ffaba7a670d7747/tensorflow/core/kernels/sparse_reduce_op.cc#L217-L228) fails to validate that each reduction group does not overflow and that each corresponding index does not point to outside the bounds of the input tensor.

### Patches
We have patched the issue in GitHub commit [87158f43f05f2720a374f3e6d22a7aaa3a33f750](https://github.com/tensorflow/tensorflow/commit/87158f43f05f2720a374f3e6d22a7aaa3a33f750). 

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cgfm-62j4-v4rf
- https://nvd.nist.gov/vuln/detail/CVE-2021-37635
- https://github.com/tensorflow/tensorflow/commit/87158f43f05f2720a374f3e6d22a7aaa3a33f750
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-548.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-746.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-257.yaml
- https://github.com/tensorflow/tensorflow
