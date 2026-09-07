# [H] Lokka: Azure Resource Manager URL path validation issue

## Summary
Severity: High
Advisory: GHSA-g2gw-q38m-vjfc
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-g2gw-q38m-vjfc
Type: github-advisory

## Affected
- npm: `@merill/lokka` — affected >=0 <2.1.2

## Details
Lokka versions prior to 2.1.2 constructed Azure Resource Manager request URLs using direct string concatenation with user-controlled path input. Specially crafted path values could alter URL authority parsing and cause Azure Resource Manager bearer tokens to be sent to an unintended host. Version 2.1.2 fixes the issue by validating Azure paths before token acquisition and constructing Azure Resource Manager URLs with the standard URL API while preserving the expected management.azure.com host.

Reported by 정해창 <haechang__@naver.com>

## References
- https://github.com/merill/lokka/security/advisories/GHSA-g2gw-q38m-vjfc
- https://github.com/merill/lokka
