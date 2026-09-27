# [H] SQL injection in funadmin

## Summary
Severity: High
Advisory: GHSA-2mv8-jjm5-f3hr
CVE: CVE-2024-48230
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-25
Source: https://github.com/advisories/GHSA-2mv8-jjm5-f3hr
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
funadmin 5.0.2 is vulnerable to SQL Injection via the parentField parameter in the index method of `\backend\controller\auth\Auth.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-48230
- https://github.com/funadmin/funadmin/issues/30
- https://github.com/funadmin/funadmin
