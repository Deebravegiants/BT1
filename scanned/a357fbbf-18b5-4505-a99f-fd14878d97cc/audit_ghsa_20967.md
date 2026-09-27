# [M] TensorFlow vulnerable to `CHECK` fail in `tf.linalg.matrix_rank`

## Summary
Severity: Medium
Advisory: GHSA-9vqj-64pv-w55c
CVE: CVE-2022-35988
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9vqj-64pv-w55c
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
When `tf.linalg.matrix_rank` receives an empty input `a`, the GPU kernel gives a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

a = tf.constant([], shape=[0, 1, 1], dtype=tf.float32)
tf.linalg.matrix_rank(a=a)
```

### Patches
We have patched the issue in GitHub commit [c55b476aa0e0bd4ee99d0f3ad18d9d706cd1260a](https://github.com/tensorflow/tensorflow/commit/c55b476aa0e0bd4ee99d0f3ad18d9d706cd1260a).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9vqj-64pv-w55c
- https://nvd.nist.gov/vuln/detail/CVE-2022-35988
- https://github.com/tensorflow/tensorflow/commit/c55b476aa0e0bd4ee99d0f3ad18d9d706cd1260a
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
