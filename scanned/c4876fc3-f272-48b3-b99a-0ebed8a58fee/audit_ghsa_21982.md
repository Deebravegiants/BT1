# [H] Integer overflows in Tensorflow

## Summary
Severity: High
Advisory: GHSA-6445-fm66-fvq2
CVE: CVE-2022-23568
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-6445-fm66-fvq2
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.5.3
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-cpu` — affected >=2.7.0 <2.7.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.5.3
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.3
- PyPI: `tensorflow-gpu` — affected >=2.7.0 <2.7.1

## Details
### Impact 
The [implementation of `AddManySparseToTensorsMap`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/sparse_tensors_map_ops.cc) is vulnerable to an integer overflow which results in a `CHECK`-fail when building new `TensorShape` objects (so, an assert failure based denial of service):

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.AddManySparseToTensorsMap(
    sparse_indices=[(0,0),(0,1),(0,2),(4,3),(5,0),(5,1)],
    sparse_values=[1,1,1,1,1,1],
    sparse_shape=[2**32,2**32],
    container='',
    shared_name='',
    name=None)
```

We are missing some validation on the shapes of the input tensors as well as directly constructing a large `TensorShape` with user-provided dimensions. The latter is an instance of [TFSA-2021-198](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/security/advisory/tfsa-2021-198.md) (CVE-2021-41197) and is easily fixed by replacing a call to `TensorShape` constructor with a call to `BuildTensorShape` static helper factory.
### Patches
We have patched the issue in GitHub commits [b51b82fe65ebace4475e3c54eb089c18a4403f1c](https://github.com/tensorflow/tensorflow/commit/b51b82fe65ebace4475e3c54eb089c18a4403f1c) and [a68f68061e263a88321c104a6c911fe5598050a8](https://github.com/tensorflow/tensorflow/commit/a68f68061e263a88321c104a6c911fe5598050a8).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-6445-fm66-fvq2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23568
- https://github.com/tensorflow/tensorflow/commit/a68f68061e263a88321c104a6c911fe5598050a8
- https://github.com/tensorflow/tensorflow/commit/b51b82fe65ebace4475e3c54eb089c18a4403f1c
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-77.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-132.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/sparse_tensors_map_ops.cc
