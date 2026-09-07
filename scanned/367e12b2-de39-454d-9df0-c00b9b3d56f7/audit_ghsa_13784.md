# [M] PHPMemcachedAdmin vulnerable to cross-site scripting (XSS) via improper encoding

## Summary
Severity: Medium
Advisory: GHSA-pr4w-m4rp-gp87
CVE: CVE-2023-6027
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-30
Source: https://github.com/advisories/GHSA-pr4w-m4rp-gp87
Type: github-advisory

## Affected
- Packagist: `elijaa/phpmemcacheadmin` — affected >=0

## Details
A critical flaw has been identified in elijaa/phpmemcachedadmin affecting version 1.3.0, specifically related to a stored XSS vulnerability. This vulnerability allows malicious actors to insert a carefully crafted JavaScript payload. The issue arises from improper encoding of user-controlled entries in the "/pmcadmin/configure.php" parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6027
- https://github.com/FriendsOfPHP/security-advisories/blob/master/elijaa/phpmemcacheadmin/CVE-2023-6027.yaml
- https://github.com/elijaa/phpmemcachedadmin
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-phpmemcachedadmin
