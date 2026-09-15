# [C] SQL Injection in Funadmin

## Summary
Severity: Critical
Advisory: GHSA-vhrv-9f9g-rfrx
CVE: CVE-2023-24781
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-vhrv-9f9g-rfrx
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
Funadmin v3.2.0 was discovered to contain a SQL injection vulnerability via the selectFields parameter at \member\MemberLevel.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24781
- https://github.com/funadmin/funadmin/issues/8
