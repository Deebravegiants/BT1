# [M] Division by 0 in `ResourceGather`

## Summary
Severity: Medium
Advisory: GHSA-qjj8-32p7-h289
CVE: CVE-2021-37653
CWE: CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qjj8-32p7-h289
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
An attacker can trigger a crash via a floating point exception in `tf.raw_ops.ResourceGather`:

```python
import tensorflow as tf

tensor = tf.constant(value=[[]],shape=(0,1),dtype=tf.uint32)
v = tf.Variable(tensor)
tf.raw_ops.ResourceGather(
  resource=v.handle,
  indices=[0],
  dtype=tf.uint32,
  batch_dims=1,
  validate_indices=False)
```

The [implementation](https://github.com/tensorflow/tensorflow/blob/f24faa153ad31a4b51578f8181d3aaab77a1ddeb/tensorflow/core/kernels/resource_variable_ops.cc#L725-L731) computes the value of a value, `batch_size`, and then divides by it without checking that this value is not 0. 

### Patches
We have patched the issue in GitHub commit  [ac117ee8a8ea57b73d34665cdf00ef3303bc0b11](https://github.com/tensorflow/tensorflow/commit/ac117ee8a8ea57b73d34665cdf00ef3303bc0b11).

The fix will be included in TensorFlow 2.6.0. We will also cherrypick this commit on TensorFlow 2.5.1, TensorFlow 2.4.3, and TensorFlow 2.3.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions. 

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qjj8-32p7-h289
- https://nvd.nist.gov/vuln/detail/CVE-2021-37653
- https://github.com/tensorflow/tensorflow/commit/ac117ee8a8ea57b73d34665cdf00ef3303bc0b11
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-566.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-764.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-275.yaml
- https://github.com/tensorflow/tensorflow
