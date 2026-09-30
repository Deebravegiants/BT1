# [M] `SparseFillEmptyRows` heap OOB

## Summary
Severity: Medium
Advisory: GHSA-rg3m-hqc5-344v
CVE: CVE-2021-41224
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-rg3m-hqc5-344v
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
The [implementation](https://github.com/tensorflow/tensorflow/blob/e71b86d47f8bc1816bf54d7bddc4170e47670b97/tensorflow/core/kernels/sparse_fill_empty_rows_op.cc#L194-L241) of `SparseFillEmptyRows` can be made to trigger a heap OOB access:

```python
import tensorflow as tf
  
data=tf.raw_ops.SparseFillEmptyRows(
  indices=[[0,0],[0,0],[0,0]],
  values=['sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss'],
  dense_shape=[5,3],
  default_value='o')
```
  
This occurs whenever the size of `indices` does not match the size of `values`.

### Patches
We have patched the issue in GitHub commit [67bfd9feeecfb3c61d80f0e46d89c170fbee682b](https://github.com/tensorflow/tensorflow/commit/67bfd9feeecfb3c61d80f0e46d89c170fbee682b).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rg3m-hqc5-344v
- https://nvd.nist.gov/vuln/detail/CVE-2021-41224
- https://github.com/tensorflow/tensorflow/commit/67bfd9feeecfb3c61d80f0e46d89c170fbee682b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-633.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-831.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-416.yaml
- https://github.com/tensorflow/tensorflow
