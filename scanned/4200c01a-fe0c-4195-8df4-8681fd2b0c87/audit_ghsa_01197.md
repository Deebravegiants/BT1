# [M] Denial of Service in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-qc53-44cj-vfvx
CVE: CVE-2020-15197
CWE: CWE-20, CWE-617
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-qc53-44cj-vfvx
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `SparseCountSparseOutput` implementation does not validate that the input arguments form a valid sparse tensor. In particular, there is no validation that the `indices` tensor has rank 2. This tensor must be a matrix because code assumes its elements are accessed as elements of a matrix:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/count_ops.cc#L185

However, malicious users can pass in tensors of different rank, resulting in a `CHECK` assertion failure and a crash. This can be used to cause denial of service in serving installations, if users are allowed to control the components of the input sparse tensor.

### Patches
We have patched the issue in 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and will release a patch release.

We recommend users to upgrade to TensorFlow 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability is a variant of [GHSA-p5f8-gfw5-33w4](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p5f8-gfw5-33w4)

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-qc53-44cj-vfvx
- https://nvd.nist.gov/vuln/detail/CVE-2020-15197
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-277.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-312.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-120.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
