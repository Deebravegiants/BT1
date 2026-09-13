# [H] Centreon Does Not Set HTTPOnly Flag

## Summary
Severity: High
Advisory: GHSA-j224-7qr4-8646
CVE: CVE-2019-17104
CWE: CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j224-7qr4-8646
Type: github-advisory

## Affected
- Packagist: `centreon/centreon` — affected >=0

## Details
In Centreon VM through 19.04.3, the cookie configuration within the Apache HTTP Server does not protect against theft because the HTTPOnly flag is not set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17104
- https://github.com/centreon/centreon-archived/issues/7097
- https://docs.centreon.com/current/en/administration/secure-platform.html#securing-the-apache-web-server
- https://github.com/centreon/centreon-archived
- https://www.openwall.com/lists/oss-security/2019/10/08/1
