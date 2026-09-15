# [C] ExecuTorch heap buffer overflow vulnerability

## Summary
Severity: Critical
Advisory: GHSA-9m39-3mf3-xwch
CVE: CVE-2025-54949
CWE: CWE-122
Ecosystem: Maven, PyPI, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-9m39-3mf3-xwch
Type: github-advisory

## Affected
- PyPI: `executorch` — affected >=0 <0.7.0
- Maven: `org.pytorch:executorch-android` — affected >=0 <0.7.0
- SwiftURL: `github.com/pytorch/executorch` — affected >=0 <0.7.0

## Details
A heap buffer overflow vulnerability in the loading of ExecuTorch models can potentially result in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit ede82493dae6d2d43f8c424e7be4721abe5242be

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54949
- https://github.com/pytorch/executorch/commit/ede82493dae6d2d43f8c424e7be4721abe5242be
- https://github.com/pytorch/executorch
- https://www.facebook.com/security/advisories/cve-2025-54949
