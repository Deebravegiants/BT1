# [M] Segfault via invalid attributes in `pywrap_tfe_src.cc`

## Summary
Severity: Medium
Advisory: GHSA-xxcj-rhqg-m46g
CVE: CVE-2022-41889
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-xxcj-rhqg-m46g
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
If a list of quantized tensors is assigned to an attribute, the pywrap code fails to parse the tensor and returns a `nullptr`, which is not caught. An example can be seen in [`tf.compat.v1.extract_volume_patches`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/generate_box_proposals_op.cu.cc) by passing in quantized tensors as input `ksizes`.
```python
import numpy as np
import tensorflow as tf

a_input = np.array([1, -1], dtype= np.int32)
a_ksizes =  a_strides = tf.constant(dtype=tf.dtypes.qint16, value=[[1, 4], [5, 2]])


tf.compat.v1.extract_volume_patches(input=a_input,ksizes=a_ksizes,strides=a_strides,padding='VALID')
```

### Patches
We have patched the issue in GitHub commit [e9e95553e5411834d215e6770c81a83a3d0866ce](https://github.com/tensorflow/tensorflow/commit/e9e95553e5411834d215e6770c81a83a3d0866ce).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattankul.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-xxcj-rhqg-m46g
- https://nvd.nist.gov/vuln/detail/CVE-2022-41889
- https://github.com/tensorflow/tensorflow/commit/e9e95553e5411834d215e6770c81a83a3d0866ce
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/image/generate_box_proposals_op.cu.cc
