# [M] Missing validation causes denial of service via `DeleteSessionTensor`

## Summary
Severity: Medium
Advisory: GHSA-h5g4-ppwx-48q2
CVE: CVE-2022-29194
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h5g4-ppwx-48q2
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
The implementation of [`tf.raw_ops.DeleteSessionTensor`](https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/session_ops.cc#L128-L144) does not fully validate the input arguments. This results in a `CHECK`-failure which can be used to trigger a denial of service attack:

```python
import tensorflow as tf

handle = tf.constant("[]", shape=[0], dtype=tf.string)
tf.raw_ops.DeleteSessionTensor(handle=handle)
```
  
The code assumes `handle` is a scalar but there is no validation for this:
  
```cc
    const Tensor& handle = ctx->input(0);
    const string& name = handle.scalar<tstring>()();
```

### Patches
We have patched the issue in GitHub commit [cff267650c6a1b266e4b4500f69fbc49cdd773c5](https://github.com/tensorflow/tensorflow/commit/cff267650c6a1b266e4b4500f69fbc49cdd773c5).

The fix will be included in TensorFlow 2.9.0. We will also cherrypick this commit on TensorFlow 2.8.1, TensorFlow 2.7.2, and TensorFlow 2.6.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Neophytos Christou from Secure Systems Lab at Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h5g4-ppwx-48q2
- https://nvd.nist.gov/vuln/detail/CVE-2022-29194
- https://github.com/tensorflow/tensorflow/commit/cff267650c6a1b266e4b4500f69fbc49cdd773c5
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/f3b9bf4c3c0597563b289c0512e98d4ce81f886e/tensorflow/core/kernels/session_ops.cc#L128-L144
- https://github.com/tensorflow/tensorflow/releases/tag/v2.6.4
- https://github.com/tensorflow/tensorflow/releases/tag/v2.7.2
- https://github.com/tensorflow/tensorflow/releases/tag/v2.8.1
- https://github.com/tensorflow/tensorflow/releases/tag/v2.9.0
