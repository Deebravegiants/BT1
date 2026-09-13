# [H] Cross-Site Request Forgery in OWASP CSRFGuard

## Summary
Severity: High
Advisory: GHSA-jx66-5ww9-m6q4
CVE: CVE-2021-28490
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jx66-5ww9-m6q4
Type: github-advisory

## Affected
- Maven: `org.owasp:csrfguard` — affected >=0 <4.0.0

## Details
In OWASP CSRFGuard through 3.1.0, CSRF can occur because the CSRF cookie may be retrieved by using only a session token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28490
- https://github.com/OWASP/www-project-csrfguard
- https://github.com/reidmefirst/vuln-disclosure/blob/main/2021-01.txt
- https://owasp.org/www-project-csrfguard
