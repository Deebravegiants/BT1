# [H] SQL injection in funadmin

## Summary
Severity: High
Advisory: GHSA-7pp4-388x-2xqj
CVE: CVE-2024-48231
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-21
Source: https://github.com/advisories/GHSA-7pp4-388x-2xqj
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin 5.0.2 is vulnerable to SQL Injection via the selectFields parameter in the index method of \app\backend\controller\auth\Auth.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48231
- https://github.com/funadmin/funadmin/issues/29
- https://github.com/funadmin/funadmin
