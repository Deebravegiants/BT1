# [C] Casdoor: GetTokenExchangeToken bypass through lack of cross-organization JWT signature check

## Summary
Severity: Critical
Advisory: GHSA-c9w5-qp6m-m395
CVE: CVE-2026-9094
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-c9w5-qp6m-m395
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0 <2.387.0

## Details
Casdoor versions 2.362.0 and earlier contain a vulnerability enabling cross-organization token exchange. The GetTokenExchangeToken function in object/token_oauth.go validates JWT signatures but does not verify that the token's user belongs to the same organization as the target application. This can result in privilege escalation across organizational boundaries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9094
- https://github.com/casdoor/casdoor/commit/d92b8568686d
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
