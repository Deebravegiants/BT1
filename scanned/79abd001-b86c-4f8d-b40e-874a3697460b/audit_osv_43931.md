# [M] phpMyFAQ 3.1.0 through 4.1.6 Authentication Bypass via LDAP

## Summary
Severity: Medium
Advisory: CVE-2026-76208
Aliases: GHSA-8pr3-q3cw-q234
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76208
Type: osv

## Details
phpMyFAQ versions 3.1.0 through 4.1.6 contain an authentication bypass vulnerability in AuthLdap::create(). When LDAP authentication is enabled, after a successful LDAP bind the code calls User::setStatus('active') unconditionally, which overwrites the account_status column of a pre-existing local account from 'blocked' to 'active'. As a result, a user whose local phpMyFAQ account has been administratively blocked can restore their account and log in by authenticating via LDAP. The state transition is not logged, so administrators cannot detect that the block was overridden. Fixed in 4.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76208.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-8pr3-q3cw-q234
- https://nvd.nist.gov/vuln/detail/CVE-2026-76208
- https://www.vulncheck.com/advisories/phpmyfaq-through-authentication-bypass-via-ldap
