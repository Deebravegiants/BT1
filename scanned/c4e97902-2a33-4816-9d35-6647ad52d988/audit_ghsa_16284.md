# [M] Onnx Out-of-bounds Read vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h8wv-9h96-m4hr
CVE: CVE-2024-27319
CWE: CWE-125
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-02-23
Source: https://github.com/advisories/GHSA-h8wv-9h96-m4hr
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.16.0

## Details
Versions of the package onnx before and including 1.15.0 are vulnerable to Out-of-bounds Read as the ONNX_ASSERT and ONNX_ASSERTM functions have an off by one string copy.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27319
- https://github.com/onnx/onnx/commit/08a399ba75a805b7813ab8936b91d0e274b08287
- https://github.com/onnx/onnx
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2024-223.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FGTBH5ZYL2LGYHIJDHN2MAUURIR5E7PY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TFJJID2IZDOLFDMWVYTBDI75ZJQC6JOL
