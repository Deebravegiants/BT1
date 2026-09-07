# [M] Overflow in `ResizeNearestNeighborGrad`

## Summary
Severity: Medium
Advisory: GHSA-368v-7v32-52fx
CVE: CVE-2022-41907
CWE: CWE-131
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-368v-7v32-52fx
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
When [`tf.raw_ops.ResizeNearestNeighborGrad`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/resize_nearest_neighbor_op.cc) is given a large `size` input, it overflows.
```
import tensorflow as tf

align_corners = True
half_pixel_centers = False
grads = tf.constant(1, shape=[1,8,16,3], dtype=tf.float16)
size = tf.constant([1879048192,1879048192], shape=[2], dtype=tf.int32)
tf.raw_ops.ResizeNearestNeighborGrad(grads=grads, size=size, align_corners=align_corners, half_pixel_centers=half_pixel_centers)
```

### Patches
We have patched the issue in GitHub commit [00c821af032ba9e5f5fa3fe14690c8d28a657624](https://github.com/tensorflow/tensorflow/commit/00c821af032ba9e5f5fa3fe14690c8d28a657624).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou from the Secure Systems Lab (SSL) at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-368v-7v32-52fx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41907
- https://github.com/tensorflow/tensorflow/commit/00c821af032ba9e5f5fa3fe14690c8d28a657624
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/resize_nearest_neighbor_op.cc
