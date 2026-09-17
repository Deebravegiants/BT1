# [M] Abort caused by allocating a vector that is too large in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-627q-g293-49q7
CVE: CVE-2022-23580
CWE: CWE-1284, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-07
Source: https://github.com/advisories/GHSA-627q-g293-49q7
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
During shape inference, TensorFlow can [allocate a large vector](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/shape_inference.cc#L788-L790) based on a value from a tensor controlled by the user:

```cc
  const auto num_dims = Value(shape_dim);
  std::vector<DimensionHandle> dims;
  dims.reserve(num_dims);
``` 
  
### Patches           
We have patched the issue in GitHub commit [1361fb7e29449629e1df94d44e0427ebec8c83c7](https://github.com/tensorflow/tensorflow/commit/1361fb7e29449629e1df94d44e0427ebec8c83c7).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-627q-g293-49q7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23580
- https://github.com/tensorflow/tensorflow/commit/1361fb7e29449629e1df94d44e0427ebec8c83c7
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-89.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-144.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/framework/shape_inference.cc#L788-L790
