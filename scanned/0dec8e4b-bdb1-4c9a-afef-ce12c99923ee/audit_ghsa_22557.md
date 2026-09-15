# [M] Missing validation causes denial of service via `StagePeek`

## Summary
Severity: Medium
Advisory: GHSA-h48f-q7rw-hvr7
CVE: CVE-2022-29195
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h48f-q7rw-hvr7
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
The implementation of [`tf.raw_ops.StagePeek`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/stage_op.cc#L261) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import tensorflow as tf

index = tf.constant([], shape=[0], dtype=tf.int32)
tf.raw_ops.StagePeek(index=index, dtypes=[tf.int32])
```
  
The code assumes `index` is a scalar but there is no validation for this before accessing its value:
  
```cc
std::size_t index = ctx->input(0).scalar<int>()();
``` 

### Patches
We have patched the issue in GitHub commit [cebe3c45d76357d201c65bdbbf0dbe6e8a63bbdb](https://github.com/tensorflow/tensorflow/commit/cebe3c45d76357d201c65bdbbf0dbe6e8a63bbdb).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h48f-q7rw-hvr7
- https://nvd.nist.gov/vuln/detail/CVE-2022-29195
- https://github.com/tensorflow/tensorflow/commit/cebe3c45d76357d201c65bdbbf0dbe6e8a63bbdb
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/stage_op.cc#L26
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
