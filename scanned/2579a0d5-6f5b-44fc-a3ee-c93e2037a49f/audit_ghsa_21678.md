# [H] Integer overflow leading to crash in Tensorflow

## Summary
Severity: High
Advisory: GHSA-x4qx-4fjv-hmw6
CVE: CVE-2022-21738
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-x4qx-4fjv-hmw6
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
The [implementation of `SparseCountSparseOutput`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/count_ops.cc#L168-L273) can be made to crash a TensorFlow process by an integer overflow whose result is then used in a memory allocation:

```python
import tensorflow as tf
import numpy as np
    
tf.raw_ops.SparseCountSparseOutput(
  indices=[[1,1]],
  values=[2],
  dense_shape=[2 ** 31, 2 ** 32],
  weights=[1],
  binary_output=True,
  minlength=-1,
  maxlength=-1,
  name=None)
```

### Patches
We have patched the issue in GitHub commit [6f4d3e8139ec724dbbcb40505891c81dd1052c4a](https://github.com/tensorflow/tensorflow/commit/6f4d3e8139ec724dbbcb40505891c81dd1052c4a).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x4qx-4fjv-hmw6
- https://nvd.nist.gov/vuln/detail/CVE-2022-21738
- https://github.com/tensorflow/tensorflow/commit/6f4d3e8139ec724dbbcb40505891c81dd1052c4a
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-62.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-117.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/count_ops.cc#L168-L273
