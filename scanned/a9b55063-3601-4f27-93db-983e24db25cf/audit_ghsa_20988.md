# [M] TensorFlow vulnerable to `CHECK` fail in `FakeQuantWithMinMaxVarsGradient`

## Summary
Severity: Medium
Advisory: GHSA-r26c-679w-mrjm
CVE: CVE-2022-36005
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-r26c-679w-mrjm
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
When `tf.quantization.fake_quant_with_min_max_vars_gradient` receives input `min` or `max` that is nonscalar, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np 
arg_0=tf.constant(value=np.random.random(size=(2, 2)), shape=(2, 2), dtype=tf.float32)
arg_1=tf.constant(value=np.random.random(size=(2, 2)), shape=(2, 2), dtype=tf.float32)
arg_2=tf.constant(value=np.random.random(size=(2, 2)), shape=(2, 2), dtype=tf.float32)
arg_3=tf.constant(value=np.random.random(size=(2, 2)), shape=(2, 2), dtype=tf.float32)
arg_4=8
arg_5=False
arg_6=''
tf.quantization.fake_quant_with_min_max_vars_gradient(gradients=arg_0, inputs=arg_1,
min=arg_2, max=arg_3, num_bits=arg_4, narrow_range=arg_5, name=arg_6)
```

### Patches
We have patched the issue in GitHub commit [f3cf67ac5705f4f04721d15e485e192bb319feed](https://github.com/tensorflow/tensorflow/commit/f3cf67ac5705f4f04721d15e485e192bb319feed).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by
 - 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology
 - Neophytos Christou, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-r26c-679w-mrjm
- https://nvd.nist.gov/vuln/detail/CVE-2022-36005
- https://github.com/tensorflow/tensorflow/commit/f3cf67ac5705f4f04721d15e485e192bb319feed
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
