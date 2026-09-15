# [M] Heap buffer overflow in Tensorflow

## Summary
Severity: Medium
Advisory: GHSA-pg59-2f92-5cph
CVE: CVE-2020-15196
CWE: CWE-119, CWE-122, CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-pg59-2f92-5cph
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `SparseCountSparseOutput` and `RaggedCountSparseOutput` implementations don't validate that the `weights` tensor has the same shape as the data. The check exists for `DenseCountSparseOutput`, where both tensors are fully specified:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/count_ops.cc#L110-L117

In the sparse and ragged count weights are still accessed in parallel with the data:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/count_ops.cc#L199-L201

But, since there is no validation, a user passing fewer weights than the values for the tensors can generate a read from outside the bounds of the heap buffer allocated for the weights.

### Patches
We have patched the issue in 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and will release a patch release.

We recommend users to upgrade to TensorFlow 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability is a variant of [GHSA-p5f8-gfw5-33w4](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p5f8-gfw5-33w4)

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-pg59-2f92-5cph
- https://nvd.nist.gov/vuln/detail/CVE-2020-15196
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-276.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-311.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-119.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
