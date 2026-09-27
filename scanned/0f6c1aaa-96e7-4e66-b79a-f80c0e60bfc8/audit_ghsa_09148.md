# [C] Casdoor doesn't verify that a JWT used for token exchange is still active

## Summary
Severity: Critical
Advisory: GHSA-339w-3hqm-9pjc
CVE: CVE-2026-9097
CWE: CWE-298
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-339w-3hqm-9pjc
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0

## Details
Casdoor versions 2.362.0 and earlier do not verify that a JWT used for token exchange is still active. The GetTokenExchangeToken() function in object/token_oauth.go validates the JWT signature and parses its claims, but never queries the Token table to verify whether the subject token has been revoked or invalidated. Because the revocation check is entirely absent, administrators are unable to terminate active sessions or revoke compromised tokens.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9097
- https://github.com/casdoor/casdoor
- https://kb.cert.org/vuls/id/780781
