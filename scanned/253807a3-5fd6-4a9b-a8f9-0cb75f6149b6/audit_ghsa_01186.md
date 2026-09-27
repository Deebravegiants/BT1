# [H] Denial of Service in Tensorflow

## Summary
Severity: High
Advisory: GHSA-x5cp-9pcf-pp3h
CVE: CVE-2020-15199
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-x5cp-9pcf-pp3h
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `RaggedCountSparseOutput` does not validate that the input arguments form a valid ragged tensor. In particular, there is no validation that the `splits` tensor has the minimum required number of elements. Code uses this quantity to initialize a different data structure:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/count_ops.cc#L241-L244

Since `BatchedMap` is equivalent to a vector, it needs to have at least one element to not be `nullptr`. If user passes a `splits` tensor that is empty or has exactly one element, we get a `SIGABRT` signal raised by the operating system.

### Patches
We have patched the issue in 3cbb917b4714766030b28eba9fb41bb97ce9ee02 and will release a patch release.

We recommend users to upgrade to TensorFlow 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability is a variant of [GHSA-p5f8-gfw5-33w4](https://github.com/tensorflow/tensorflow/security/advisories/GHSA-p5f8-gfw5-33w4)

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-x5cp-9pcf-pp3h
- https://nvd.nist.gov/vuln/detail/CVE-2020-15199
- https://github.com/tensorflow/tensorflow/commit/3cbb917b4714766030b28eba9fb41bb97ce9ee02
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-279.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-314.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-122.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
