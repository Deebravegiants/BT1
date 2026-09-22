# [C] PHPMemcachedAdmin Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-8qfm-h8rh-h3r7
CVE: CVE-2023-6026
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-8qfm-h8rh-h3r7
Type: github-advisory

## Affected
- Packagist: `elijaa/phpmemcacheadmin` — affected >=0

## Details
A Path traversal vulnerability has been reported in elijaa/phpmemcachedadmin affecting version 1.3.0. This vulnerability allows an attacker to delete files stored on the server due to lack of proper verification of user-supplied input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6026
- https://github.com/FriendsOfPHP/security-advisories/blob/master/elijaa/phpmemcacheadmin/CVE-2023-6026.yaml
- https://github.com/elijaa/phpmemcachedadmin
- https://packagist.org/packages/elijaa/phpmemcacheadmin
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-phpmemcachedadmin
