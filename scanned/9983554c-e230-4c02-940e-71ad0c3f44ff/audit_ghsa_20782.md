# [M] TensorFlow vulnerable to `CHECK` failure in `AvgPoolOp`

## Summary
Severity: Medium
Advisory: GHSA-mgmh-g2v6-mqw5
CVE: CVE-2022-35941
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-mgmh-g2v6-mqw5
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.2

## Details
### Impact
The [`AvgPoolOp`](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/avgpooling_op.cc#L56-L98) function takes an argument `ksize` that must be positive but is not checked. A negative `ksize` can trigger a `CHECK` failure and crash the program.
```python
import tensorflow as tf
import numpy as np

value = np.ones([1, 1, 1, 1])
ksize = [1, 1e20, 1, 1]
strides = [1, 1, 1, 1]
padding = 'SAME'
data_format = 'NHWC'

tf.raw_ops.AvgPool(value=value, ksize=ksize, strides=strides, padding=padding, data_format=data_format)
```

### Patches
We have patched the issue in GitHub commit [3a6ac52664c6c095aa2b114e742b0aa17fdce78f](https://github.com/tensorflow/tensorflow/commit/3a6ac52664c6c095aa2b114e742b0aa17fdce78f).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jingyi Shi.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mgmh-g2v6-mqw5
- https://nvd.nist.gov/vuln/detail/CVE-2022-35941
- https://github.com/tensorflow/tensorflow/commit/3a6ac52664c6c095aa2b114e742b0aa17fdce78f
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/avgpooling_op.cc#L56-L98
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
