# [H] Open Neural Network Exchange (ONNX) Path Traversal Vulnerability

## Summary
Severity: High
Advisory: GHSA-h36j-8vv3-cj52
CVE: CVE-2024-7776
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-h36j-8vv3-cj52
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.17.0

## Details
A vulnerability in the `download_model` function of the onnx/onnx framework, before and including version 1.16.1, allows for arbitrary file overwrite due to inadequate prevention of path traversal attacks in malicious tar files. This vulnerability can be exploited by an attacker to overwrite files in the user's directory, potentially leading to remote command execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7776
- https://github.com/onnx/onnx/pull/6222
- https://github.com/onnx/onnx/commit/1b70f9b673259360b6a2339c4bd97db9ea6e552f
- https://github.com/onnx/onnx
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2025-10.yaml
- https://huntr.com/bounties/a7a46cf6-1fa0-454b-988c-62d222e83f63
