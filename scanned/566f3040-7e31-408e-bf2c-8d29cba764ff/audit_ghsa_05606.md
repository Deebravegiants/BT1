# [H] Aimeos contains a SQL injection vulnerability in the json api 'sort' parameter

## Summary
Severity: High
Advisory: GHSA-hm9j-cgmm-2w36
CVE: CVE-2021-47763
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-hm9j-cgmm-2w36
Type: github-advisory

## Affected
- Packagist: `aimeos/aimeos-laravel` — affected 2021.10

## Details
Aimeos 2021.10 LTS contains a SQL injection vulnerability in the json api 'sort' parameter that allows attackers to inject malicious database queries. Attackers can manipulate the sort parameter to reveal table and column names by sending crafted GET requests to the jsonapi/review endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-47763
- https://aimeos.org
- https://aimeos.org/laravel-ecommerce-package
- https://github.com/aimeos/aimeos-laravel
- https://www.exploit-db.com/exploits/50538
