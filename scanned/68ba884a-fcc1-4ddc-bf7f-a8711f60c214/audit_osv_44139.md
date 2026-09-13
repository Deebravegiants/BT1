# [M] Kimai before 2.58.0 Authentication Bypass via Password Reset Link

## Summary
Severity: Medium
Advisory: CVE-2026-80196
Aliases: GHSA-m492-gv72-xvxj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-80196
Type: osv

## Details
Kimai before 2.58.0 contains an authentication bypass vulnerability where password reset links remain valid after password changes because the LoginLink signature covers only the user id, not the password hash. Attackers who intercept or cache a password reset link can use it up to 2 additional times within a 1-hour window to log in as the user even after the legitimate user has changed their password.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80196.json
- https://github.com/kimai/kimai/security/advisories/GHSA-m492-gv72-xvxj
- https://nvd.nist.gov/vuln/detail/CVE-2026-80196
- https://www.vulncheck.com/advisories/kimai-before-2.58.0-authentication-bypass-via-password-reset-link
