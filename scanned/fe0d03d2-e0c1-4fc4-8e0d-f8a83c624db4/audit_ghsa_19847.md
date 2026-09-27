# [M] Pimcore Vulnerable to SQL Injection in getRelationFilterCondition

## Summary
Severity: Medium
Advisory: GHSA-qjpx-5m2p-5pgh
CVE: CVE-2025-27617
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-qjpx-5m2p-5pgh
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.4

## Details
### Summary
Authenticated users can craft a filter string used to cause a SQL injection.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._
This code does not look to sanitize inputs: https://github.com/pimcore/pimcore/blob/c721a42c23efffd4ca916511ddb969598d302396/models/DataObject/ClassDefinition/Data/Extension/RelationFilterConditionParser.php#L29-L47

c.f. with https://github.com/pimcore/pimcore/blob/c721a42c23efffd4ca916511ddb969598d302396/models/DataObject/ClassDefinition/Data/Multiselect.php#L332-L347

### PoC
_Complete instructions, including specific configuration details, to reproduce the vulnerability._

### Impact
_What kind of vulnerability is it? Who is impacted?_

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-qjpx-5m2p-5pgh
- https://nvd.nist.gov/vuln/detail/CVE-2025-27617
- https://github.com/pimcore/pimcore/commit/19a8520895484e68fd254773e32476565d91deea
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/blob/c721a42c23efffd4ca916511ddb969598d302396/models/DataObject/ClassDefinition/Data/Extension/RelationFilterConditionParser.php#L29-L47
- https://github.com/pimcore/pimcore/blob/c721a42c23efffd4ca916511ddb969598d302396/models/DataObject/ClassDefinition/Data/Multiselect.php#L332-L347
