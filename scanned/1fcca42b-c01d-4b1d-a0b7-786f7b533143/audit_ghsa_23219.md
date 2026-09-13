# [M] Log value insertion in craftercms

## Summary
Severity: Medium
Advisory: GHSA-545f-pgp7-fwjf
CVE: CVE-2021-23266
CWE: CWE-116
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-545f-pgp7-fwjf
Type: github-advisory

## Affected
- Maven: `org.craftercms:craftercms` — affected >=3.1.0 <3.1.18

## Details
An anonymous user can craft a URL with text that ends up in the log viewer as is. The text can then include textual messages to mislead the administrator.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23266
- https://docs.craftercms.org/en/3.1/security/advisory.html#cv-2022051602
