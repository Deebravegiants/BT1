# [M] TensorFlow vulnerable to `CHECK` fail in `tf.sparse.cross`

## Summary
Severity: Medium
Advisory: GHSA-p7hr-f446-x6qf
CVE: CVE-2022-35997
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-p7hr-f446-x6qf
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-cpu` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.7.2
- PyPI: `tensorflow-gpu` — affected >=2.8.0 <2.8.1

## Details
### Impact
If `tf.sparse.cross` receives an input `separator` that is not a scalar, it gives a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

tf.sparse.cross(inputs=[],name='a',separator=tf.constant(['a', 'b'],dtype=tf.string))
```

### Patches
We have patched the issue in GitHub commit [83dcb4dbfa094e33db084e97c4d0531a559e0ebf](https://github.com/tensorflow/tensorflow/commit/83dcb4dbfa094e33db084e97c4d0531a559e0ebf).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p7hr-f446-x6qf
- https://nvd.nist.gov/vuln/detail/CVE-2022-35997
- https://github.com/tensorflow/tensorflow/commit/83dcb4dbfa094e33db084e97c4d0531a559e0ebf
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
