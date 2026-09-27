# [M] TensorFlow vulnerable to `CHECK` fail in `RandomPoissonV2`

## Summary
Severity: Medium
Advisory: GHSA-cv2p-32v3-vhwq
CVE: CVE-2022-36003
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-cv2p-32v3-vhwq
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
When `RandomPoissonV2` receives large input shape and rates, it gives a `CHECK` fail that can trigger a denial of service attack.
```python
import tensorflow as tf
arg_0=tf.random.uniform(shape=(4,), dtype=tf.int32, maxval=65536)
arg_1=tf.random.uniform(shape=(4, 4, 4, 4, 4), dtype=tf.float32, maxval=None)
arg_2=0
arg_3=0
arg_4=tf.int32
arg_5=None
tf.raw_ops.RandomPoissonV2(shape=arg_0, rate=arg_1, seed=arg_2,
                           seed2=arg_3, dtype=arg_4, name=arg_5)
```

### Patches
We have patched the issue in GitHub commit [552bfced6ce4809db5f3ca305f60ff80dd40c5a3](https://github.com/tensorflow/tensorflow/commit/552bfced6ce4809db5f3ca305f60ff80dd40c5a3).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by 刘力源, Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-cv2p-32v3-vhwq
- https://nvd.nist.gov/vuln/detail/CVE-2022-36003
- https://github.com/tensorflow/tensorflow/commit/552bfced6ce4809db5f3ca305f60ff80dd40c5a3
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
