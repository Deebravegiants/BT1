# [C] SQL injection vulnerability in Meshery

## Summary
Severity: Critical
Advisory: GHSA-9jjc-grg5-67gj
CVE: CVE-2023-46575
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-24
Source: https://github.com/advisories/GHSA-9jjc-grg5-67gj
Type: github-advisory

## Affected
- Go: `github.com/layer5io/meshery` — affected >=0 <0.6.179

## Details
A SQL injection vulnerability in Meshery before 0.6.179 allows a remote attacker to obtain sensitive information and execute arbitrary code via the order parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46575
- https://github.com/meshery/meshery/pull/9372
- https://github.com/meshery/meshery/commit/ffe00967acfe4444a5db08ff3a4cafb9adf6013f
- https://github.com/meshery/meshery
- https://github.com/meshery/meshery/compare/v0.6.178...v0.6.179
- https://meshery.io
