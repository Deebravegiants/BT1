# [M] Division by 0 in `ResourceScatterDiv`

## Summary
Severity: Medium
Advisory: GHSA-ch4f-829c-v5pw
CVE: CVE-2021-37642
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-ch4f-829c-v5pw
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
The implementation of `tf.raw_ops.ResourceScatterDiv` is vulnerable to a division by 0 error:

```python
import tensorflow as tf

v= tf.Variable([1,2,3])
tf.raw_ops.ResourceScatterDiv(
  resource=v.handle,
  indices=[1],
  updates=[0])
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/8d72537c6abf5a44103b57b9c2e22c14f5f49698/tensorflow/core/kernels/resource_variable_ops.cc#L865) uses a common class for all binary operations but fails to treat the division by 0 case separately.

### Patches
We have patched the issue in GitHub commit [4aacb30888638da75023e6601149415b39763d76](https://github.com/tensorflow/tensorflow/commit/4aacb30888638da75023e6601149415b39763d76).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-ch4f-829c-v5pw
- https://nvd.nist.gov/vuln/detail/CVE-2021-37642
- https://github.com/tensorflow/tensorflow/commit/4aacb30888638da75023e6601149415b39763d76
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-555.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-753.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-264.yaml
- https://github.com/tensorflow/tensorflow
