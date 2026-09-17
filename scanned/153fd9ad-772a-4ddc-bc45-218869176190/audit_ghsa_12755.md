# [C] CakePHP Database\\Query::offset() and limit() methods are vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-6g8q-qfpv-57wp
CVE: CVE-2023-22727
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-6g8q-qfpv-57wp
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=4.2.0 <4.2.12
- Packagist: `cakephp/cakephp` — affected >=4.3.0 <4.3.11
- Packagist: `cakephp/cakephp` — affected >=4.4.0 <4.4.10
- Packagist: `cakephp/database` — affected >=4.2.0 <4.2.12
- Packagist: `cakephp/database` — affected >=4.3.0 <4.3.11
- Packagist: `cakephp/database` — affected >=4.4.0 <4.4.10

## Details
### Impact

The `Cake\Database\Query::limit()` and `Cake\Database\Query::offset()` methods are vulnerable to SQL injection if passed un-sanitized user request data.

### Patches
This issue has been fixed in 4.2.12, 4.3.11, 4.4.10

### Workarounds

Using CakePHP's Pagination library will mitigate this issue, as will validating or casting parameters to these methods.

### References

https://bakery.cakephp.org/2023/01/06/cakephp_4211_4311_4410_released.html

## References
- https://github.com/cakephp/cakephp/security/advisories/GHSA-6g8q-qfpv-57wp
- https://nvd.nist.gov/vuln/detail/CVE-2023-22727
- https://github.com/cakephp/cakephp/commit/3f463e7084b5a15e67205ced3a622577cca7a239
- https://bakery.cakephp.org/2023/01/06/cakephp_4211_4311_4410_released.html
- https://github.com/cakephp/cakephp
