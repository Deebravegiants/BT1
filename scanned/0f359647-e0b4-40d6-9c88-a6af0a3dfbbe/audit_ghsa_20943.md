# [M] TensorFlow vulnerable to `CHECK` failure in tf.reshape via overflows

## Summary
Severity: Medium
Advisory: GHSA-f4w6-h4f5-wx45
CVE: CVE-2022-35934
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-f4w6-h4f5-wx45
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
The implementation of tf.reshape op in TensorFlow is vulnerable to a denial of service via CHECK-failure (assertion failure) caused by overflowing the number of elements in a tensor:
```python
import tensorflow as tf

tf.reshape(tensor=[[1]],shape=tf.constant([0 for i in range(255)], dtype=tf.int64))
```
This is another instance of [TFSA-2021-198](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md) (https://github.com/advisories/GHSA-prcg-wp5q-rv7p).

### Patches
We have patched the issue in GitHub commit [61f0f9b94df8c0411f0ad0ecc2fec2d3f3c33555](https://github.com/tensorflow/tensorflow/commit/61f0f9b94df8c0411f0ad0ecc2fec2d3f3c33555).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Kang Hong Jin from Singapore Management University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-f4w6-h4f5-wx45
- https://nvd.nist.gov/vuln/detail/CVE-2022-35934
- https://github.com/tensorflow/tensorflow/commit/61f0f9b94df8c0411f0ad0ecc2fec2d3f3c33555
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
