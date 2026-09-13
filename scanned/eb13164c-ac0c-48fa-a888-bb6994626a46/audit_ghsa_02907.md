# [M] Overflow/crash in `tf.tile` when tiling tensor is large

## Summary
Severity: Medium
Advisory: GHSA-2p25-55c9-h58q
CVE: CVE-2021-41198
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-2p25-55c9-h58q
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
If `tf.tile` is called with a large input argument then the TensorFlow process will crash due to a `CHECK`-failure caused by an overflow.

```python
import tensorflow as tf
import numpy as np
tf.keras.backend.tile(x=np.ones((1,1,1)), n=[100000000,100000000, 100000000])
```

The number of elements in the output tensor is too much for the `int64_t` type and the overflow is detected via a `CHECK` statement. This aborts the process.

### Patches
We have patched the issue in GitHub commit [9294094df6fea79271778eb7e7ae1bad8b5ef98f](https://github.com/tensorflow/tensorflow/commit/9294094df6fea79271778eb7e7ae1bad8b5ef98f) (merging [#51138](https://github.com/tensorflow/tensorflow/pull/51138)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46911).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-2p25-55c9-h58q
- https://nvd.nist.gov/vuln/detail/CVE-2021-41198
- https://github.com/tensorflow/tensorflow/issues/46911
- https://github.com/tensorflow/tensorflow/commit/9294094df6fea79271778eb7e7ae1bad8b5ef98f
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-608.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-806.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-391.yaml
- https://github.com/tensorflow/tensorflow
