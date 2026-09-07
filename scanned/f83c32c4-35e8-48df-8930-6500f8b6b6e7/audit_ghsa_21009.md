# [M] TensorFlow vulnerable to floating point exception in `Conv2D`

## Summary
Severity: Medium
Advisory: GHSA-q5jv-m6qw-5g37
CVE: CVE-2022-35996
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-q5jv-m6qw-5g37
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
If `Conv2D` is given empty `input` and the `filter` and `padding` sizes are valid, the output is all-zeros. This causes division-by-zero floating point exceptions that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np
with tf.device("CPU"): # also can be triggerred on GPU
   input = np.ones([1, 0, 2, 1])
   filter = np.ones([1, 1, 1, 1])
   strides = ([1, 1, 1, 1])
   padding = "EXPLICIT"
   explicit_paddings = [0 , 0, 1, 1, 1, 1, 0, 0]
   data_format = "NHWC"
   res = tf.raw_ops.Conv2D(
       input=input,
       filter=filter,
       strides=strides,
       padding=padding,
        explicit_paddings=explicit_paddings,
       data_format=data_format,
  )
```

### Patches
We have patched the issue in GitHub commit [611d80db29dd7b0cfb755772c69d60ae5bca05f9](https://github.com/tensorflow/tensorflow/commit/611d80db29dd7b0cfb755772c69d60ae5bca05f9).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Jingyi Shi.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q5jv-m6qw-5g37
- https://nvd.nist.gov/vuln/detail/CVE-2022-35996
- https://github.com/tensorflow/tensorflow/commit/611d80db29dd7b0cfb755772c69d60ae5bca05f9
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
