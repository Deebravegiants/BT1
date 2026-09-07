# [M] TensorFlow vulnerable to `CHECK` fail in `TensorListFromTensor`

## Summary
Severity: Medium
Advisory: GHSA-9v8w-xmr4-wgxp
CVE: CVE-2022-35992
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9v8w-xmr4-wgxp
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
When `TensorListFromTensor` receives an `element_shape` of a rank greater than one, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=tf.random.uniform(shape=(6, 6, 2), dtype=tf.bfloat16, maxval=None)
arg_1=tf.random.uniform(shape=(6, 9, 1, 3), dtype=tf.int64, maxval=65536)
arg_2=''
tf.raw_ops.TensorListFromTensor(tensor=arg_0, element_shape=arg_1, name=arg_2)
```

### Patches
We have patched the issue in GitHub commit [3db59a042a38f4338aa207922fa2f476e000a6ee](https://github.com/tensorflow/tensorflow/commit/3db59a042a38f4338aa207922fa2f476e000a6ee).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-9v8w-xmr4-wgxp
- https://nvd.nist.gov/vuln/detail/CVE-2022-35992
- https://github.com/tensorflow/tensorflow/commit/3db59a042a38f4338aa207922fa2f476e000a6ee
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
