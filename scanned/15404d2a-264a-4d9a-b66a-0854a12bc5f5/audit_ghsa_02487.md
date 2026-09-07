# [M] Floating point exception in `SparseDenseCwiseDiv`

## Summary
Severity: Medium
Advisory: GHSA-hp4c-x6r7-6555
CVE: CVE-2021-37636
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hp4c-x6r7-6555
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <2.3.4
- PyPI: `tensorflow` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-cpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-cpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.1
- PyPI: `tensorflow-gpu` — affected >=0 <2.3.4
- PyPI: `tensorflow-gpu` — affected >=2.4.0 <2.4.3
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.1

## Details
### Impact
The implementation of `tf.raw_ops.SparseDenseCwiseDiv` is vulnerable to a division by 0 error:

```python
import tensorflow as tf
import numpy as np

tf.raw_ops.SparseDenseCwiseDiv( 
  sp_indices=np.array([[4]]),
  sp_values=np.array([-400]),
  sp_shape=np.array([647.]),
  dense=np.array([0]))
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/a1bc56203f21a5a4995311825ffaba7a670d7747/tensorflow/core/kernels/sparse_dense_binary_op_shared.cc#L56) uses a common class for all binary operations but fails to treat the division by 0 case separately.

### Patches
We have patched the issue in GitHub commit [d9204be9f49520cdaaeb2541d1dc5187b23f31d9](https://github.com/tensorflow/tensorflow/commit/d9204be9f49520cdaaeb2541d1dc5187b23f31d9).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-hp4c-x6r7-6555
- https://nvd.nist.gov/vuln/detail/CVE-2021-37636
- https://github.com/tensorflow/tensorflow/commit/d9204be9f49520cdaaeb2541d1dc5187b23f31d9
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-549.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-747.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-258.yaml
- https://github.com/tensorflow/tensorflow
