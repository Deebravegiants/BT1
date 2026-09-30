# [H] SQL Injection in Admin Translations API

## Summary
Severity: High
Advisory: GHSA-jwg4-qcgv-5wg6
CVE: CVE-2023-30850
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-jwg4-qcgv-5wg6
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
SQL injection is a web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. It generally allows an attacker to view data that they are not normally able to retrieve. This might include data belonging to other users, or any other data that the application itself is able to access. 

In many cases, an attacker can modify or delete this data, causing persistent changes to the application's content or behavior. In some situations, an attacker can escalate an SQL injection attack to compromise the underlying server or other back-end infrastructure, or perform a denial-of-service attack. It was observed that the reported API endpoint accessible by an authenticated administrator user and is vulnerable to SQL injection via the "filter" POST parameter. The parameter accepts JSON formatted data. The value of JSON key "property" inside "filter" is not sanitized properly and is used in a SQL statement in an unsafe manner, resulting in SQL injection.

### Patches
Update to version 10.5.21 or apply this patch manually https://github.com/pimcore/pimcore/commit/7e32cc28145274ddfc30fb791012d26c1278bd38.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/7e32cc28145274ddfc30fb791012d26c1278bd38.patch manually.

### References
https://github.com/pimcore/pimcore/pull/14952

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-jwg4-qcgv-5wg6
- https://nvd.nist.gov/vuln/detail/CVE-2023-30850
- https://github.com/pimcore/pimcore/pull/14952
- https://github.com/pimcore/pimcore/commit/7e32cc28145274ddfc30fb791012d26c1278bd38
- https://github.com/pimcore/pimcore/commit/7e32cc28145274ddfc30fb791012d26c1278bd38.patch
- https://github.com/pimcore/pimcore
