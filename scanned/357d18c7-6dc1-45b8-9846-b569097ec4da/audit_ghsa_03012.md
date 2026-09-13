# [H] Incomplete validation of shapes in multiple TF ops

## Summary
Severity: High
Advisory: GHSA-pgcq-h79j-2f69
CVE: CVE-2021-41206
CWE: CWE-354
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-pgcq-h79j-2f69
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow` — affected >=0 <2.4.4
- PyPI: `tensorflow-cpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-cpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-cpu` — affected >=0 <2.4.4
- PyPI: `tensorflow-gpu` — affected >=2.6.0 <2.6.1
- PyPI: `tensorflow-gpu` — affected >=2.5.0 <2.5.2
- PyPI: `tensorflow-gpu` — affected >=0 <2.4.4

## Details
### Impact
Several TensorFlow operations are missing validation for the shapes of the tensor arguments involved in the call. Depending on the API, this can result in undefined behavior and segfault or `CHECK`-fail related crashes but in some scenarios writes and reads from heap populated arrays are also possible.

We have discovered these issues internally via tooling while working on improving/testing GPU op determinism. As such, we don't have reproducers and there will be multiple fixes for these issues.

### Patches
We have patched the issue in GitHub commits [68422b215e618df5ad375bcdc6d2052e9fd3080a](https://github.com/tensorflow/tensorflow/commit/68422b215e618df5ad375bcdc6d2052e9fd3080a), [4d74d8a00b07441cba090a02e0dd9ed385145bf4](https://github.com/tensorflow/tensorflow/commit/4d74d8a00b07441cba090a02e0dd9ed385145bf4), [579261dcd446385831fe4f7457d802a59685121d](https://github.com/tensorflow/tensorflow/commit/579261dcd446385831fe4f7457d802a59685121d), [da4aad5946be30e5f049920fa076e1f7ef021261](https://github.com/tensorflow/tensorflow/commit/da4aad5946be30e5f049920fa076e1f7ef021261), [4dddb2fd0b01cdd196101afbba6518658a2c9e07](https://github.com/tensorflow/tensorflow/commit/4dddb2fd0b01cdd196101afbba6518658a2c9e07), and [e7f497570abb6b4ae5af4970620cd880e4c0c904](https://github.com/tensorflow/tensorflow/commit/e7f497570abb6b4ae5af4970620cd880e4c0c904).

These fixes will be included in TensorFlow 2.7.0. We will also cherrypick these commits on TensorFlow 2.6.1, TensorFlow 2.5.2, and TensorFlow 2.4.4, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pgcq-h79j-2f69
- https://nvd.nist.gov/vuln/detail/CVE-2021-41206
- https://github.com/tensorflow/tensorflow/commit/4d74d8a00b07441cba090a02e0dd9ed385145bf4
- https://github.com/tensorflow/tensorflow/commit/4dddb2fd0b01cdd196101afbba6518658a2c9e07
- https://github.com/tensorflow/tensorflow/commit/579261dcd446385831fe4f7457d802a59685121d
- https://github.com/tensorflow/tensorflow/commit/68422b215e618df5ad375bcdc6d2052e9fd3080a
- https://github.com/tensorflow/tensorflow/commit/da4aad5946be30e5f049920fa076e1f7ef021261
- https://github.com/tensorflow/tensorflow/commit/e7f497570abb6b4ae5af4970620cd880e4c0c904
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2021-845.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2021-847.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2021-843.yaml
- https://github.com/tensorflow/tensorflow
