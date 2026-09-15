# [C] ExecuTorch out-of-bounds access vulnerability

## Summary
Severity: Critical
Advisory: GHSA-f9hx-c6jf-3qxm
CVE: CVE-2025-54950
CWE: CWE-125
Ecosystem: Maven, PyPI, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-f9hx-c6jf-3qxm
Type: github-advisory

## Affected
- PyPI: `executorch` — affected >=0 <0.7.0
- Maven: `org.pytorch:executorch-android` — affected >=0 <0.7.0
- SwiftURL: `github.com/pytorch/executorch` — affected >=0 <0.7.0

## Details
An out-of-bounds access vulnerability in the loading of ExecuTorch models can cause the runtime to crash and potentially result in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit fb03b6f85596a8f954d97929075335255b6a58d4.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54950
- https://github.com/pytorch/executorch/commit/b6b7a16df5e7852d976d8c34c8a7e9a1b6f7d005
- https://github.com/pytorch/executorch/commit/fb03b6f85596a8f954d97929075335255b6a58d4
- https://github.com/pytorch/executorch
- https://www.facebook.com/security/advisories/cve-2025-54950
