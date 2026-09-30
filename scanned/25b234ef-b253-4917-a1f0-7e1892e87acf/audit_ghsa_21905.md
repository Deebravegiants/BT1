# [H] Improper Validation of Integrity Check Value in TensorFlow

## Summary
Severity: High
Advisory: GHSA-43q8-3fv7-pr5x
CWE: CWE-354
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-43q8-3fv7-pr5x
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact
The implementation of [`tf.sparse.split`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/sparse_split_op.cc#L26-L102) does not fully validate the input arguments. Hence, a malicious user can trigger a denial of service via a segfault or a heap OOB read:

```python
import tensorflow as tf
data = tf.random.uniform([1, 32, 32], dtype=tf.float32)
axis = [1, 2]
x = tf.sparse.from_dense(data)
result = tf.sparse.split(x,3, axis=axis)
```
The code assumes `axis` is a scalar. This is another instance of [TFSA-2021-190](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-190.md) (CVE-2021-41206).

### Patches
We have patched the issue in GitHub commit [61bf91e768173b001d56923600b40d9a95a04ad5](https://github.com/tensorflow/tensorflow/commit/61bf91e768173b001d56923600b40d9a95a04ad5) (merging [#53695](https://github.com/tensorflow/tensorflow/pull/53695)).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/53660).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-43q8-3fv7-pr5x
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pgcq-h79j-2f69
- https://github.com/tensorflow/tensorflow/pull/53695
- https://github.com/tensorflow/tensorflow/commit/61bf91e768173b001d56923600b40d9a95a04ad5
- https://github.com/tensorflow/tensorflow
