# [H] Uninitialized variable access in Tensorflow

## Summary
Severity: High
Advisory: GHSA-q85f-69q7-55h2
CVE: CVE-2022-23573
CWE: CWE-908
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-q85f-69q7-55h2
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
The [implementation of `AssignOp`](https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/assign_op.h#L30-L143) can result in copying unitialized data to a new tensor. This later results in undefined behavior.

The implementation has a check that the left hand side of the assignment is initialized (to minimize number of allocations), but does not check that the right hand side is also initialized.
  
### Patches
We have patched the issue in GitHub commit [ef1d027be116f25e25bb94a60da491c2cf55bd0b](https://github.com/tensorflow/tensorflow/commit/ef1d027be116f25e25bb94a60da491c2cf55bd0b).
    
The fix will be included in TensorFlow 2.8.0. We will also cherrypick this commit on TensorFlow 2.7.1, TensorFlow 2.6.3, and TensorFlow 2.5.3, as these are also affected and still in supported range.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-q85f-69q7-55h2
- https://nvd.nist.gov/vuln/detail/CVE-2022-23573
- https://github.com/tensorflow/tensorflow/commit/ef1d027be116f25e25bb94a60da491c2cf55bd0b
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2022-82.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2022-137.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/blob/a1320ec1eac186da1d03f033109191f715b2b130/tensorflow/core/kernels/assign_op.h#L30-L143
