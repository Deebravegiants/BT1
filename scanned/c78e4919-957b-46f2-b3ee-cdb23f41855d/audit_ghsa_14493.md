# [H] TensorFlow has Null Pointer Error in TensorArrayConcatV2

## Summary
Severity: High
Advisory: GHSA-64jg-wjww-7c5w
CVE: CVE-2023-25663
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-64jg-wjww-7c5w
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
When ctx->step_containter() is a null ptr, the Lookup function will be executed with a null pointer.
```python
import tensorflow as tf
tf.raw_ops.TensorArrayConcatV2(handle=['a', 'b'], flow_in = 0.1, dtype=tf.int32, element_shape_except0=1)
```

### Patches
We have patched the issue in GitHub commit [239139d2ae6a81ae9ba499ad78b56d9b2931538a](https://github.com/tensorflow/tensorflow/commit/239139d2ae6a81ae9ba499ad78b56d9b2931538a).

The fix will be included in TensorFlow 2.12.0. We will also cherrypick this commit on TensorFlow 2.11.1


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Yu Tian

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-64jg-wjww-7c5w
- https://nvd.nist.gov/vuln/detail/CVE-2023-25663
- https://github.com/tensorflow/tensorflow/commit/239139d2ae6a81ae9ba499ad78b56d9b2931538a
- https://github.com/tensorflow/tensorflow
