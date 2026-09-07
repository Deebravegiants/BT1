# [M] php-mod/curl allows Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-f8p3-q834-q9cj
CVE: CVE-2021-30134
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-26
Source: https://github.com/advisories/GHSA-f8p3-q834-q9cj
Type: github-advisory

## Affected
- Packagist: `php-mod/curl` — affected >=0 <2.3.2

## Details
php-mod/curl (a wrapper of the PHP cURL extension) before 2.3.2 allows XSS via the `post_file_path_upload.php` key parameter and the POST data to `post_multidimensional.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30134
- https://github.com/php-mod/curl/commit/0bddefe8bbd292065f23dd6e24d2c745c4865cf7
- https://github.com/php-mod/curl
- https://wpscan.com/vulnerability/0b547728-27d2-402e-ae17-90d539344ec7
