# [M] Incomplete validation in `MaxPoolGrad`

## Summary
Severity: Medium
Advisory: GHSA-7ghq-fvr3-pj2x
CVE: CVE-2021-37674
CWE: CWE-1284, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7ghq-fvr3-pj2x
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
An attacker can trigger a denial of service via a segmentation fault in `tf.raw_ops.MaxPoolGrad` caused by missing validation:

```python
import tensorflow as tf
  
tf.raw_ops.MaxPoolGrad(
  orig_input = tf.constant([], shape=[3, 0, 0, 2], dtype=tf.float32),
  orig_output = tf.constant([], shape=[3, 0, 0, 2], dtype=tf.float32),
  grad = tf.constant([], shape=[3, 0, 0, 2], dtype=tf.float32),
  ksize = [1, 16, 16, 1],
  strides = [1, 16, 18, 1],
  padding = "EXPLICIT",
  explicit_paddings = [0, 0, 14, 3, 15, 5, 0, 0])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/kernels/maxpooling_op.cc) misses some validation for the `orig_input` and `orig_output` tensors.

The fixes for [CVE-2021-29579](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-068.md) were incomplete.
                                                                                                                                                                                                                                                                                          
### Patches
We have patched the issue in GitHub commit [136b51f10903e044308cf77117c0ed9871350475](https://github.com/tensorflow/tensorflow/commit/136b51f10903e044308cf77117c0ed9871350475).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-7ghq-fvr3-pj2x
- https://nvd.nist.gov/vuln/detail/CVE-2021-37674
- https://github.com/tensorflow/tensorflow/commit/136b51f10903e044308cf77117c0ed9871350475
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-587.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-785.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-296.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-068.md
