# [M] TensorFlow vulnerable to `CHECK` fail in `EmptyTensorList`

## Summary
Severity: Medium
Advisory: GHSA-qhw4-wwr7-gjc5
CVE: CVE-2022-35998
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-qhw4-wwr7-gjc5
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.7.2
- PyPI: `tensorflow` — affected >=2.8.0 <2.8.1
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.1

## Details
### Impact
If `EmptyTensorList` receives an input `element_shape` with more than one dimension, it gives a `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf

tf.raw_ops.EmptyTensorList(element_shape=tf.ones(dtype=tf.int32, shape=[1, 0]), max_num_elements=tf.constant(1),element_dtype=tf.int32)
```

### Patches
We have patched the issue in GitHub commit [c8ba76d48567aed347508e0552a257641931024d](https://github.com/tensorflow/tensorflow/commit/c8ba76d48567aed347508e0552a257641931024d).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qhw4-wwr7-gjc5
- https://nvd.nist.gov/vuln/detail/CVE-2022-35998
- https://github.com/tensorflow/tensorflow/commit/c8ba76d48567aed347508e0552a257641931024d
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
