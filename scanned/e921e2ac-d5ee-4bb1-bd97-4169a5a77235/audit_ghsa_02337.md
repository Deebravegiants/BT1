# [M] Reference binding to nullptr in `RaggedTensorToSparse`

## Summary
Severity: Medium
Advisory: GHSA-4xfp-4pfp-89wg
CVE: CVE-2021-37656
CWE: CWE-824
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-4xfp-4pfp-89wg
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
An attacker can cause undefined behavior via binding a reference to null pointer in `tf.raw_ops.RaggedTensorToSparse`:

```python
import tensorflow as tf

tf.raw_ops.RaggedTensorToSparse(
  rt_nested_splits=[[0, 38, 0]],
  rt_dense_values=[])
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/ragged_tensor_to_sparse_kernel.cc#L30) has an incomplete validation of the splits values: it does not check that they are in increasing order.

### Patches
We have patched the issue in GitHub commit [1071f554dbd09f7e101324d366eec5f4fe5a3ece](https://github.com/tensorflow/tensorflow/commit/1071f554dbd09f7e101324d366eec5f4fe5a3ece).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-4xfp-4pfp-89wg
- https://nvd.nist.gov/vuln/detail/CVE-2021-37656
- https://github.com/tensorflow/tensorflow/commit/1071f554dbd09f7e101324d366eec5f4fe5a3ece
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-569.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-767.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-278.yaml
- https://github.com/tensorflow/tensorflow
