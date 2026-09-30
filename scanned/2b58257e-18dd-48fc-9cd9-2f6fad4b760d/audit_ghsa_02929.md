# [M] Overflow/crash in `tf.image.resize` when size is large

## Summary
Severity: Medium
Advisory: GHSA-5hx2-qx8j-qjqm
CVE: CVE-2021-41199
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-5hx2-qx8j-qjqm
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
If `tf.image.resize` is called with a large input argument then the TensorFlow process will crash due to a `CHECK`-failure caused by an overflow.

```python
import tensorflow as tf
import numpy as np

tf.keras.layers.UpSampling2D(
  size=1610637938,
  data_format='channels_first',
  interpolation='bilinear')(np.ones((5,1,1,1)))
```

The number of elements in the output tensor is too much for the `int64_t` type and the overflow is detected via a `CHECK` statement. This aborts the process.

### Patches
We have patched the issue in GitHub commit [e5272d4204ff5b46136a1ef1204fc00597e21837](https://github.com/tensorflow/tensorflow/commit/e5272d4204ff5b46136a1ef1204fc00597e21837) (merging [#51497](https://github.com/tensorflow/tensorflow/pull/51497)).

The fix will be included in TensorFlow 2.7.0. We will also cherrypick this commit on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported externally via a [GitHub issue](https://github.com/tensorflow/tensorflow/issues/46914).

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-5hx2-qx8j-qjqm
- https://nvd.nist.gov/vuln/detail/CVE-2021-41199
- https://github.com/tensorflow/tensorflow/issues/46914
- https://github.com/tensorflow/tensorflow/commit/e5272d4204ff5b46136a1ef1204fc00597e21837
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-609.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-807.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-392.yaml
- https://github.com/tensorflow/tensorflow
