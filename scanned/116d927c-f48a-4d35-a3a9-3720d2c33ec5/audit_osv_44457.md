# [H] Rodauth before 2.46.0 Authentication Bypass via webauthn_login

## Summary
Severity: High
Advisory: CVE-2026-82466
Aliases: GHSA-3pvr-v35r-4r75
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82466
Type: osv

## Details
Rodauth before 2.46.0 contains an authentication bypass vulnerability in the webauthn_login route that allows logged-in users to authenticate as any other account. Attackers can exploit improper account resolution logic that falls back to session account identifiers instead of validating the credential binding to complete authentication as arbitrary users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82466.json
- https://github.com/jeremyevans/rodauth/security/advisories/GHSA-3pvr-v35r-4r75
- https://nvd.nist.gov/vuln/detail/CVE-2026-82466
- https://www.vulncheck.com/advisories/rodauth-before-2.46.0-authentication-bypass-via-webauthn-login
- https://github.com/jeremyevans/rodauth/commit/35d74a9f07b2005a8ea75fc11a6539c04f3c2840
- https://github.com/jeremyevans/rodauth
