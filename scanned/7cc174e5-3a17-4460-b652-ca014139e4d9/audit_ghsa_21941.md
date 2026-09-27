# [H] Undefined behavior in `SparseTensorSliceDataset`

## Summary
Severity: High
Advisory: GHSA-pfjj-m3jj-9jc9
CVE: CVE-2022-21736
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-pfjj-m3jj-9jc9
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
The [implementation of `SparseTensorSliceDataset`](https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/data/sparse_tensor_slice_dataset_op.cc#L227-L292) has an undefined behavior: under certain condition it can be made to dereference a `nullptr` value:

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.SparseTensorSliceDataset(
  indices=[[]],
  values=[],
  dense_shape=[1,1])
```

The 3 input arguments represent a sparse tensor. However, there are some preconditions that these arguments must satisfy but these are not validated in the implementation.

### Patches
We have patched the issue in GitHub commit [965b97e4a9650495cda5a8c210ef6684b4b9eceb](https://github.com/tensorflow/tensorflow/commit/965b97e4a9650495cda5a8c210ef6684b4b9eceb).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by Faysal Hossain Shezan from University of Virginia.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pfjj-m3jj-9jc9
- https://nvd.nist.gov/vuln/detail/CVE-2022-21736
- https://github.com/tensorflow/tensorflow/commit/965b97e4a9650495cda5a8c210ef6684b4b9eceb
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-60.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-115.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/5100e359aef5c8021f2e71c7b986420b85ce7b3d/tensorflow/core/kernels/data/sparse_tensor_slice_dataset_op.cc#L227-L292
