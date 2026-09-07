# [M] WPGlobus plugin Stored XSS & CSRF security vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qf99-3qrg-g97q
CVE: CVE-2018-5367
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qf99-3qrg-g97q
Type: github-advisory

## Affected
- Packagist: `wpglobus/wpglobus` — affected >=0 <1.9.7

## Details
The WPGlobus plugin 1.9.6 for WordPress has XSS via the `wpglobus_option[post_type][post]` parameter to `wp-admin/options.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-5367
- https://github.com/WPGlobus/WPGlobus
- https://github.com/d4wner/Vulnerabilities-Report/blob/master/wpglobus.md
- https://wpvulndb.com/vulnerabilities/9003
