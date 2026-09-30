# [H] pimcore/customer-management-framework-bundle has SQL Injection vulnerability in Segment Assignment query

## Summary
Severity: High
Advisory: GHSA-25fx-3c2q-cq46
CVE: CVE-2023-2756
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-17
Source: https://github.com/advisories/GHSA-25fx-3c2q-cq46
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.3.10

## Details
### Impact
An administrator user can use the inheritable segments feature to execute his own blind SQL queries.

A user with administrator privileges can run any SQL query on database. This can be used to retrieve sensitive data, change database information or any other malicious activity against the database.

### Patches
Update to version 3.3.10 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/76df151737b7964ce5169fdf9e27a0ad801757fe.patch

### Workarounds
Apply https://github.com/pimcore/customer-data-framework/commit/76df151737b7964ce5169fdf9e27a0ad801757fe.patch manually.

### References
https://huntr.dev/bounties/cf398528-819f-456e-88e7-c06d268d3f44/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-25fx-3c2q-cq46
- https://nvd.nist.gov/vuln/detail/CVE-2023-2756
- https://github.com/pimcore/customer-data-framework/commit/76df151737b7964ce5169fdf9e27a0ad801757fe
- https://github.com/pimcore/customer-data-framework
- https://huntr.dev/bounties/cf398528-819f-456e-88e7-c06d268d3f44
