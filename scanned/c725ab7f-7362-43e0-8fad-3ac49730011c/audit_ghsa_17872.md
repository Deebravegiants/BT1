# [C] ExecuTorch integer overflow vulnerability

## Summary
Severity: Critical
Advisory: GHSA-84m3-f99p-cqx5
CVE: CVE-2025-30405
CWE: CWE-190
Ecosystem: Maven, PyPI, SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-84m3-f99p-cqx5
Type: github-advisory

## Affected
- PyPI: `executorch` — affected >=0 <0.7.0
- Maven: `org.pytorch:executorch-android` — affected >=0 <0.7.0
- SwiftURL: `github.com/pytorch/executorch` — affected >=0 <0.7.0

## Details
An integer overflow vulnerability in the loading of ExecuTorch models can cause objects to be placed outside their allocated memory area, potentially resulting in code execution or other undesirable effects. This issue affects ExecuTorch prior to commit 0830af8207240df8d7f35b984cdf8bc35d74fa73.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-30405
- https://github.com/pytorch/executorch/commit/0830af8207240df8d7f35b984cdf8bc35d74fa73
- https://github.com/pytorch/executorch
- https://www.facebook.com/security/advisories/cve-2025-30405
