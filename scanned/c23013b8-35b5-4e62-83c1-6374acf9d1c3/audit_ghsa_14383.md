# [C] Funadmin vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-jx2x-fg9p-7gc7
CVE: CVE-2023-24774
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-jx2x-fg9p-7gc7
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin v3.2.0 was discovered to contain a SQL injection vulnerability via the selectFields parameter at \controller\auth\Auth.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24774
- https://github.com/funadmin/funadmin/issues/12
- https://github.com/funadmin/funadmin
