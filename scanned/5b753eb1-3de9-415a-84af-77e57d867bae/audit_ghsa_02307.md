# [M] Missing validation in shape inference for `Dequantize`

## Summary
Severity: Medium
Advisory: GHSA-qfpc-5pjr-mh26
CVE: CVE-2021-37677
CWE: CWE-1284, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qfpc-5pjr-mh26
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
The shape inference code for `tf.raw_ops.Dequantize` has a vulnerability that could trigger a denial of service via a segfault if an attacker provides invalid arguments:

```python
import tensorflow as tf

tf.compat.v1.disable_v2_behavior()
tf.raw_ops.Dequantize(
  input_tensor = tf.constant(-10.0, dtype=tf.float32),
  input_tensor = tf.cast(input_tensor, dtype=tf.quint8),
  min_range = tf.constant([], shape=[0], dtype=tf.float32),
  max_range = tf.constant([], shape=[0], dtype=tf.float32),
  mode  = 'MIN_COMBINED',
  narrow_range=False,
  axis=-10,
  dtype=tf.dtypes.float32)
```

The shape inference [implementation](https://github.com/tensorflow/tensorflow/blob/460e000de3a83278fb00b61a16d161b1964f15f4/tensorflow/core/ops/array_ops.cc#L2999-L3014) uses `axis` to select between two different values for `minmax_rank` which is then used to retrieve tensor dimensions. However, code assumes that `axis` can be either `-1` or a value greater than `-1`, with no validation for the other values.

### Patches
We have patched the issue in GitHub commit [da857cfa0fde8f79ad0afdbc94e88b5d4bbec764](https://github.com/tensorflow/tensorflow/commit/da857cfa0fde8f79ad0afdbc94e88b5d4bbec764).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Yakun Zhang of Baidu Security.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qfpc-5pjr-mh26
- https://nvd.nist.gov/vuln/detail/CVE-2021-37677
- https://github.com/tensorflow/tensorflow/commit/da857cfa0fde8f79ad0afdbc94e88b5d4bbec764
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-590.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-788.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-299.yaml
- https://github.com/tensorflow/tensorflow
