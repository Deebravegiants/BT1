# [M] `CHECK` fail via inputs in `PyFunc`

## Summary
Severity: Medium
Advisory: GHSA-mv77-9g28-cwg3
CVE: CVE-2022-41908
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-21
Source: https://github.com/advisories/GHSA-mv77-9g28-cwg3
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
An input `token` that is not a UTF-8 bytestring will trigger a `CHECK` fail in [`tf.raw_ops.PyFunc`](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/lib/core/py_func.cc).

```python
import tensorflow as tf

value = tf.constant(value=[1,2])
token = b'\xb0'
dataType = [tf.int32]

tf.raw_ops.PyFunc(input=value,token=token,Tout=dataType)
```

### Patches
We have patched the issue in GitHub commit [9f03a9d3bafe902c1e6beb105b2f24172f238645](https://github.com/tensorflow/tensorflow/commit/9f03a9d3bafe902c1e6beb105b2f24172f238645).

The fix will be included in TensorFlow 2.11. We will also cherrypick this commit on TensorFlow 2.10.1, 2.9.3, and TensorFlow 2.8.4, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by pattarakritr@smu.edu.sg

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mv77-9g28-cwg3
- https://nvd.nist.gov/vuln/detail/CVE-2022-41908
- https://github.com/tensorflow/tensorflow/commit/9f03a9d3bafe902c1e6beb105b2f24172f238645
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/master/tensorflow/python/lib/core/py_func.cc
