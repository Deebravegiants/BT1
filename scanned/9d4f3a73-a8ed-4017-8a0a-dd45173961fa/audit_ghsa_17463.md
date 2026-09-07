# [M] Algernon Cross-Site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8jqm-8qm3-qgqm
CVE: CVE-2025-65754
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-8jqm-8qm3-qgqm
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.5

## Details
Cross-site Scripting vulnerability in Algernon v1.17.4 allows attackers to execute arbitrary code via injecting a crafted payload into a filename.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65754
- https://github.com/xyproto/algernon/commit/cd8832014a624a9aeab60566434c3344135e23f8
- https://gist.github.com/Bnyt7/0faa90ff93c5d98093a0e29a1eb34d81
- https://github.com/Bnyt7/CVE-2025-65754
- https://github.com/xyproto/algernon
