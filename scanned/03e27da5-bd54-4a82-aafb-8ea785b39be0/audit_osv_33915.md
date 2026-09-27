# [M] EspoCRM vulnerable to LDAP Injection through Improper Neutralization of Special Elements

## Summary
Severity: Medium
Advisory: CVE-2025-52575
Aliases: GHSA-rjm8-77fr-4f3v
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-07-21
Source: https://osv.dev/vulnerability/CVE-2025-52575
Type: osv

## Details
EspoCRM is an Open Source CRM (Customer Relationship Management) software. EspoCRM versions 9.1.6 and earlier are vulnerable to blind LDAP Injection when LDAP authentication is enabled. A remote, unauthenticated attacker can manipulate LDAP queries by injecting crafted input containing wildcard characters (e.g., *). This may allow the attacker to bypass authentication controls, enumerate valid usernames, or retrieve sensitive directory information depending on the LDAP server configuration. This was fixed in version 9.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52575.json
- https://github.com/espocrm/espocrm/security/advisories/GHSA-rjm8-77fr-4f3v
- https://nvd.nist.gov/vuln/detail/CVE-2025-52575
- https://github.com/espocrm/espocrm/commit/8649f1ac0ce714b2c31727bca3dd95d06e17337f
