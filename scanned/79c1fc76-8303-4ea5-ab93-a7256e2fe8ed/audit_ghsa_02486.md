# [M] Integer division by 0 in sparse reshaping

## Summary
Severity: Medium
Advisory: GHSA-95xm-g58g-3p88
CVE: CVE-2021-37640
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-95xm-g58g-3p88
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
The implementation of `tf.raw_ops.SparseReshape` can be made to trigger an integral division by 0 exception:

```python
import tensorflow as tf

tf.raw_ops.SparseReshape(
  input_indices = np.ones((1,3)),
  input_shape = np.array([1,1,0]),
  new_shape = np.array([1,0]))
```
  
The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/reshape_util.cc#L176-L181) calls the reshaping functor whenever there is at least an index in the input but does not check that shape of the input or the target shape have both a non-zero number of elements.

The [reshape functor](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/reshape_util.cc#L40-L78) blindly divides by the dimensions of the target shape. Hence, if this is not checked, code will result in a division by 0.
  
### Patches
We have patched the issue in GitHub commit [4923de56ec94fff7770df259ab7f2288a74feb41](https://github.com/tensorflow/tensorflow/commit/4923de56ec94fff7770df259ab7f2288a74feb41).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1 as this is the other affected version.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.
  
### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-95xm-g58g-3p88
- https://nvd.nist.gov/vuln/detail/CVE-2021-37640
- https://github.com/tensorflow/tensorflow/commit/4923de56ec94fff7770df259ab7f2288a74feb41
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-553.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-751.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-262.yaml
- https://github.com/tensorflow/tensorflow
