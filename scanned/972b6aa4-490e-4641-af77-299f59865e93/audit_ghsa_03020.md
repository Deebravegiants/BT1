# [M] Cross-site Scripting in tempura

## Summary
Severity: Medium
Advisory: GHSA-w4v7-hwx7-9929
CVE: CVE-2021-23784
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-w4v7-hwx7-9929
Type: github-advisory

## Affected
- npm: `tempura` — affected >=0 <0.4.0

## Details
This affects the package tempura before 0.4.0. If the input to the esc function is of type object (i.e an array) it is returned without being escaped/sanitized, leading to a potential Cross-Site Scripting vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23784
- https://github.com/lukeed/tempura/commit/58a5c3671e2f36b26810e77ead9e0dd471902f9b
- https://github.com/lukeed/tempura
- https://github.com/lukeed/tempura/releases/tag/v0.4.0
- https://snyk.io/vuln/SNYK-JS-TEMPURA-1569633
