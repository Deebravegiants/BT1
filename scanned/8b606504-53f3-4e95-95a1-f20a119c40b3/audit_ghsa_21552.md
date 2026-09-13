# [M] Seg fault in `ndarray_tensor_bridge` due to zero and large inputs

## Summary
Severity: Medium
Advisory: GHSA-jq6x-99hj-q636
CVE: CVE-2022-41884
CWE: CWE-670
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-jq6x-99hj-q636
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.8.4
- PyPI: `tensorflow` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-gpu` — affected >=0 <2.8.4
- PyPI: `tensorflow-cpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-gpu` — affected >=2.9.0 <2.9.3
- PyPI: `tensorflow-cpu` — affected >=2.10.0 <2.10.1
- PyPI: `tensorflow-gpu` — affected >=2.10.0 <2.10.1

## Details
### Impact
If a numpy array is created with a shape such that one element is zero and the others sum to a large number, an error will be raised. E.g. the following raises an error:
```python
np.ones((0, 2**31, 2**31))
```
An example of a proof of concept:
```python
import numpy as np
import tensorflow as tf

input_val = tf.constant([1])
shape_val = np.array([i for i in range(21)])

tf.broadcast_to(input=input_val,shape=shape_val)
```
The return value of `PyArray_SimpleNewFromData`, which returns null on such shapes, is not checked.

### Patches
We have patched the issue in GitHub commit [2b56169c16e375c521a3bc8ea658811cc0793784](https://github.com/tensorflow/tensorflow/commit/2b56169c16e375c521a3bc8ea658811cc0793784).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattanukul.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jq6x-99hj-q636
- https://nvd.nist.gov/vuln/detail/CVE-2022-41884
- https://github.com/tensorflow/tensorflow/commit/2b56169c16e375c521a3bc8ea658811cc0793784
- https://github.com/tensorflow/tensorflow
