# [H] Integer overflow in Tensorflow

## Summary
Severity: High
Advisory: GHSA-wm93-f238-7v37
CVE: CVE-2022-23576
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-wm93-f238-7v37
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
The [implementation of `OpLevelCostEstimator::CalculateOutputSize`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L1598-L1617) is vulnerable to an integer overflow if an attacker can create an operation which would involve tensors with large enough number of elements:
```cc
for (const auto& dim : output_shape.dim()) {
  output_size *= dim.size();
} 
```
  
Here, we can have a large enough number of dimensions in `output_shape.dim()` or just a small number of dimensions being large enough to cause an overflow in the multiplication.

### Patches
We have patched the issue in GitHub commit [b9bd6cfd1c50e6807846af9a86f9b83cafc9c8ae](https://github.com/tensorflow/tensorflow/commit/b9bd6cfd1c50e6807846af9a86f9b83cafc9c8ae).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information 
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-wm93-f238-7v37
- https://nvd.nist.gov/vuln/detail/CVE-2022-23576
- https://github.com/tensorflow/tensorflow/commit/b9bd6cfd1c50e6807846af9a86f9b83cafc9c8ae
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-85.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-140.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L1598-L1617
