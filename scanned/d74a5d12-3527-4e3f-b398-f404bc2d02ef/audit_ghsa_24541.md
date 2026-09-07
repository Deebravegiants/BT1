# [M] Integer overflow in `SpaceToBatchND`

## Summary
Severity: Medium
Advisory: GHSA-jjm6-4vf7-cjh4
CVE: CVE-2022-29203
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jjm6-4vf7-cjh4
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.6.4
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
The implementation of `tf.raw_ops.SpaceToBatchND` (in all backends such as XLA and handwritten kernels) is vulnerable to an integer overflow:

```python
import tensorflow as tf

input = tf.constant(-3.5e+35, shape=[10,19,22], dtype=tf.float32)
block_shape = tf.constant(-1879048192, shape=[2], dtype=tf.int64)
paddings = tf.constant(0, shape=[2,2], dtype=tf.int32)
tf.raw_ops.SpaceToBatchND(input=input, block_shape=block_shape, paddings=paddings)
```

The result of this integer overflow is used to allocate the output tensor, hence we get a denial of service via a `CHECK`-failure (assertion failure), as in [TFSA-2021-198](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md).

### Patches
We have patched the issue in GitHub commit [acd56b8bcb72b163c834ae4f18469047b001fadf](https://github.com/tensorflow/tensorflow/commit/acd56b8bcb72b163c834ae4f18469047b001fadf).
  
The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.
  
### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jjm6-4vf7-cjh4
- https://nvd.nist.gov/vuln/detail/CVE-2022-29203
- https://github.com/tensorflow/tensorflow/commit/acd56b8bcb72b163c834ae4f18469047b001fadf
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
