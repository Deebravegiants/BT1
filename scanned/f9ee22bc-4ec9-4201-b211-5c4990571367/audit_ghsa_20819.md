# [M] TensorFlow vulnerable to `CHECK` failures in `UnbatchGradOp`

## Summary
Severity: Medium
Advisory: GHSA-h5vq-gw2c-pq47
CVE: CVE-2022-35952
CWE: CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-h5vq-gw2c-pq47
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
The [`UnbatchGradOp`](https://github.com/tensorflow/tensorflow/blob/769eddaf479c8debead9a59a72617d6ed6f0fe10/tensorflow/core/kernels/batch_kernels.cc#L891) function takes an argument `id` that is assumed to be a scalar. A nonscalar `id` can trigger a `CHECK` failure and crash the program.
```python
import numpy as np
import tensorflow as tf

# `id` is not scalar
tf.raw_ops.UnbatchGrad(original_input= tf.constant([1]),batch_index=tf.constant([[0,0,0 ], ], dtype=tf.int64),grad=tf.constant([1,]),id=tf.constant([1,1,], dtype=tf.int64))
```
It also requires its argument `batch_index` to contain three times the number of elements as indicated in its `batch_index.dim_size(0)`. An incorrect `batch_index` can trigger a `CHECK` failure and crash the program.
```python
import numpy as np
import tensorflow as tf

# batch_index's size is not 3
tf.raw_ops.UnbatchGrad(original_input= tf.constant([1]),batch_index=tf.constant([[0,0], ], dtype=tf.int64),grad=tf.constant([1,]),id=tf.constant([1,], dtype=tf.int64))
```

### Patches
We have patched the issue in GitHub commit [5f945fc6409a3c1e90d6970c9292f805f6e6ddf2](https://github.com/tensorflow/tensorflow/commit/5f945fc6409a3c1e90d6970c9292f805f6e6ddf2).

The fix will be included in TensorFlow 2.10.0. We will also cherrypick this commit on TensorFlow 2.9.1, TensorFlow 2.8.1, and TensorFlow 2.7.2, as these are also affected and still in supported range.


### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.


### Attribution
This vulnerability has been reported by Kang Hong Jin from Singapore Management University and 刘力源 from the Information System & Security and Countermeasures Experiments Center, Beijing Institute of Technology

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h5vq-gw2c-pq47
- https://nvd.nist.gov/vuln/detail/CVE-2022-35952
- https://github.com/tensorflow/tensorflow/commit/5f945fc6409a3c1e90d6970c9292f805f6e6ddf2
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/769eddaf479c8debead9a59a72617d6ed6f0fe10/tensorflow/core/kernels/batch_kernels.cc#L891
- https://github.com/tensorflow/tensorflow/releases/tag/v2.10.0
