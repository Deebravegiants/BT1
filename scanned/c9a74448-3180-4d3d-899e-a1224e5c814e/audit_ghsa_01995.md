# [C] SQL Injection in NukeViet

## Summary
Severity: Critical
Advisory: GHSA-q4qv-fmwc-qxpx
CVE: CVE-2019-7726
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-q4qv-fmwc-qxpx
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.3.04

## Details
modules/banners/funcs/click.php in NukeViet before 4.3.04 has a SQL INSERT statement with raw header data from an HTTP request (e.g., Referer and User-Agent).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7726
- https://github.com/nukeviet/nukeviet/pull/2740/commits/05dfb9b4531f12944fe39556f58449b9a56241be
- https://github.com/nukeviet/nukeviet/blob/4.3.04/CHANGELOG.txt
- https://github.com/nukeviet/nukeviet/blob/nukeviet4.3/CHANGELOG.txt
- https://github.com/nukeviet/nukeviet/compare/4.3.03...4.3.04
