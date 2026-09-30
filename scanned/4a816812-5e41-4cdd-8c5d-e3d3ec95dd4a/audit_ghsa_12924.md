# [H] Directory Traversal in onnx

## Summary
Severity: High
Advisory: GHSA-ffxj-547x-5j7c
CVE: CVE-2022-25882
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-26
Source: https://github.com/advisories/GHSA-ffxj-547x-5j7c
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.13.0

## Details
Versions of the package onnx before 1.13.0 are vulnerable to Directory Traversal as the external_data field of the tensor proto can have a path to the file which is outside the model current directory or user-provided directory, for example "../../../etc/passwd"

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25882
- https://github.com/onnx/onnx/issues/3991
- https://github.com/onnx/onnx/pull/4400
- https://github.com/onnx/onnx/commit/f369b0e859024095d721f1d1612da5a8fa38988d
- https://gist.github.com/jnovikov/02a9aff9bf2188033e77bd91ff062856
- https://github.com/onnx/onnx
- https://github.com/onnx/onnx/blob/96516aecd4c110b0ac57eba08ac236ebf7205728/onnx/checker.cc%23L129
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2023-38.yaml
- https://security.snyk.io/vuln/SNYK-PYTHON-ONNX-2395479
