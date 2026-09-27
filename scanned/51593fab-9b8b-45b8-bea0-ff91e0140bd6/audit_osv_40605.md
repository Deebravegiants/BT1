# [H] Perry < 0.5.1166 JWT Expiration Bypass via verify_decode

## Summary
Severity: High
Advisory: CVE-2026-53776
Aliases: GHSA-5324-c68v-8w62
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-53776
Type: osv

## Details
Perry before 0.5.1166 contains a JWT validation vulnerability that allows remote attackers to bypass token expiration by exploiting the unconditional setting of validate_exp = false in the verify_decode helper within the stdlib JWT verification path. Attackers in possession of a previously issued bearer token can present expired tokens to any jwt.verify() call and retain authenticated access indefinitely, bypassing force-expired sessions such as user logout or administrative revocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53776.json
- https://github.com/PerryTS/perry/releases/v0.5.1166
- https://github.com/PerryTS/perry/security/advisories/GHSA-5324-c68v-8w62
- https://nvd.nist.gov/vuln/detail/CVE-2026-53776
- https://www.vulncheck.com/advisories/perry-jwt-expiration-bypass-via-verify-decode
- https://github.com/PerryTS/perry
