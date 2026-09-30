# [H] z-push/z-push-dev SQL Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-w832-w3p8-cw29
CVE: CVE-2025-8264
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-29
Source: https://github.com/advisories/GHSA-w832-w3p8-cw29
Type: github-advisory

## Affected
- Packagist: `z-push/z-push-dev` — affected >=0 <2.7.6

## Details
Versions of the package z-push/z-push-dev before 2.7.6 are vulnerable to SQL Injection due to unparameterized queries in the IMAP backend. An attacker can inject malicious commands by manipulating the username field in basic authentication. This allows the attacker to access and potentially modify or delete sensitive data from a linked third-party database. 

**Note:** This vulnerability affects Z-Push installations that utilize the IMAP backend and have the IMAP_FROM_SQL_QUERY option configured. 

 Mitigation
Change configuration to use the default or LDAP in backend/imap/config.php

php
define('IMAP_DEFAULTFROM', '');

or
php
define('IMAP_DEFAULTFROM', 'ldap');

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8264
- https://github.com/Z-Hub/Z-Push/pull/161
- https://github.com/Z-Hub/Z-Push/pull/161/commits/f981d515a35ac4c303959af21dce880a5db02786
- https://github.com/Z-Hub/Z-Push/commit/deb044a40e97dab1814da9aa8330c0a590957fc5
- https://github.com/Z-Hub/Z-Push
- https://github.com/Z-Hub/Z-Push/blob/af25a2169a50d6e05a5916d1e8b2b6cd17011c98/src/backend/imap/user_identity.php%23L211C9-L214C25
- https://security.snyk.io/vuln/SNYK-PHP-ZPUSHZPUSHDEV-10908180
- https://xbow.com/blog/xbow-zpush-sqli
