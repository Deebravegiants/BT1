# [M] `CHECK_EQ` fail in `tf.raw_ops.TensorListResize`

## Summary
Severity: Medium
Advisory: GHSA-67pf-62xr-q35m
CVE: CVE-2022-41893
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-67pf-62xr-q35m
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
If [`tf.raw_ops.TensorListResize`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/list_kernels.cc) is given a nonscalar value for input `size`, it results `CHECK` fail which can be used to trigger a denial of service attack.
```python
import numpy as np
import tensorflow as tf

a = data_structures.tf_tensor_list_new(elements = tf.constant(value=[3, 4, 5]))
b = np.zeros([0, 2, 3, 3])

tf.raw_ops.TensorListResize(input_handle=a, size=b)
```

### Patches
We have patched the issue in GitHub commit [888e34b49009a4e734c27ab0c43b0b5102682c56](https://github.com/tensorflow/tensorflow/commit/888e34b49009a4e734c27ab0c43b0b5102682c56).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Pattarakrit Rattankul

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-67pf-62xr-q35m
- https://nvd.nist.gov/vuln/detail/CVE-2022-41893
- https://github.com/tensorflow/tensorflow/commit/888e34b49009a4e734c27ab0c43b0b5102682c56
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/kernels/list_kernels.cc
