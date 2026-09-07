# [M] Overflow in `tf.keras.losses.poisson`

## Summary
Severity: Medium
Advisory: GHSA-8fvv-46hw-vpg3
CVE: CVE-2022-41887
CWE: CWE-131
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-8fvv-46hw-vpg3
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
[`tf.keras.losses.poisson`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/keras/losses.py) receives a `y_pred` and `y_true` that are passed through `functor::mul` in [`BinaryOp`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/cwise_ops_common.h). If the resulting dimensions overflow an `int32`, TensorFlow will crash due to a size mismatch during broadcast assignment.
```python
import numpy as np
import tensorflow as tf

true_value = tf.reshape(shape=[1, 2500000000], tensor = tf.zeros(dtype=tf.bool, shape=[50000, 50000]))
pred_value = np.array([[[-2]], [[8]]], dtype = np.float64)

tf.keras.losses.poisson(y_true=true_value,y_pred=pred_value)
```

### Patches
We have patched the issue in GitHub commit [c5b30379ba87cbe774b08ac50c1f6d36df4ebb7c](https://github.com/tensorflow/tensorflow/commit/c5b30379ba87cbe774b08ac50c1f6d36df4ebb7c).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1 and 2.9.3, as these are also affected and still in supported range. However, we will not cherrypick this commit into TensorFlow 2.8.x, as it depends on Eigen behavior that changed between 2.8 and 2.9.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattankul.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-8fvv-46hw-vpg3
- https://nvd.nist.gov/vuln/detail/CVE-2022-41887
- https://github.com/tensorflow/tensorflow/commit/c5b30379ba87cbe774b08ac50c1f6d36df4ebb7c
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/cwise_ops_common.h
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/keras/losses.py
