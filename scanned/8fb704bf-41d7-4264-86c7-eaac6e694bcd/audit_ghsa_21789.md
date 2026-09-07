# [H] Integer overflow in Tensorflow

## Summary
Severity: High
Advisory: GHSA-c94w-c95p-phf8
CVE: CVE-2022-23575
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-c94w-c95p-phf8
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
The [implementation of `OpLevelCostEstimator::CalculateTensorSize`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L1552-L1558) is vulnerable to an integer overflow if an attacker can create an operation which would involve a tensor with large enough number of elements:
```cc
int64_t OpLevelCostEstimator::CalculateTensorSize(
    const OpInfo::TensorProperties& tensor, bool* found_unknown_shapes) {
  int64_t count = CalculateTensorElementCount(tensor, found_unknown_shapes);
  int size = DataTypeSize(BaseType(tensor.dtype()));
  VLOG(2) << "Count: " << count << " DataTypeSize: " << size;
  return count * size;
}
```
Here, `count` and `size` can be large enough to cause `count * size` to overflow.

### Patches
We have patched the issue in GitHub commit [fcd18ce3101f245b083b30655c27b239dc72221e](https://github.com/tensorflow/tensorflow/commit/fcd18ce3101f245b083b30655c27b239dc72221e).

The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-c94w-c95p-phf8
- https://nvd.nist.gov/vuln/detail/CVE-2022-23575
- https://github.com/tensorflow/tensorflow/commit/fcd18ce3101f245b083b30655c27b239dc72221e
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-84.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-139.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/grappler/costs/op_level_cost_estimator.cc#L1552-L1558
