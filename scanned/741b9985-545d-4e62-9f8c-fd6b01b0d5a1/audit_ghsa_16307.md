# [H] Onnx Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-whh8-fjgc-qp73
CVE: CVE-2024-27318
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-23
Source: https://github.com/advisories/GHSA-whh8-fjgc-qp73
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.16.0

## Details
Versions of the package onnx before and including 1.15.0 are vulnerable to Directory Traversal as the external_data field of the tensor proto can have a path to the file which is outside the model current directory or user-provided directory. The vulnerability occurs as a bypass for the patch added for CVE-2022-25882.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27318
- https://github.com/onnx/onnx/commit/66b7fb630903fdcf3e83b6b6d56d82e904264a20
- https://github.com/onnx/onnx
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2024-222.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FGTBH5ZYL2LGYHIJDHN2MAUURIR5E7PY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TFJJID2IZDOLFDMWVYTBDI75ZJQC6JOL
- https://security.snyk.io/vuln/SNYK-PYTHON-ONNX-2395479
