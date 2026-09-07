# [M] Data leakage via SQL Injection in Pimcore

## Summary
Severity: Medium
Advisory: GHSA-fpff-384j-vxq7
CVE: CVE-2019-10763
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-fpff-384j-vxq7
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <6.3.0

## Details
pimcore/pimcore before 6.3.0 is vulnerable to SQL Injection. An attacker with limited privileges (classes permission) can achieve a SQL injection that can lead in data leakage. The vulnerability can be exploited via 'id', 'storeId', 'pageSize' and 'tables' parameters, using a payload for trigger a time based or error based sql injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10763
- https://blog.certimetergroup.com/it/articolo/security/sql_injection_in_pimcore_6.2.3
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-480391
