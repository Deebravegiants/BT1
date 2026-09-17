# [H] Snipe-IT before 8.7.0 Authentication Bypass via SAML Username Collation

## Summary
Severity: High
Advisory: CVE-2026-86770
Aliases: GHSA-w3vv-5wxh-xg4h
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-86770
Type: osv

## Details
Snipe-IT before 8.7.0 fails to validate username case sensitivity during SAML authentication, allowing attackers to authenticate as different users by registering IdP accounts with accent or case variants of victim usernames. Attackers can exploit the default utf8mb4_unicode_ci database collation to bypass username matching and achieve account takeover through federated login paths including SAML, LDAP, and OAuth.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86770.json
- https://github.com/grokability/snipe-it/security/advisories/GHSA-w3vv-5wxh-xg4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-86770
- https://www.vulncheck.com/advisories/snipe-it-before-8.7.0-authentication-bypass-via-saml-username-collation
