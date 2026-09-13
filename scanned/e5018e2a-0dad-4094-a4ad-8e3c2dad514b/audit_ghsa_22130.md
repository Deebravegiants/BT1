# [C] php-shellcommand command injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-c7fv-wv9f-cgjw
CVE: CVE-2019-10774
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-c7fv-wv9f-cgjw
Type: github-advisory

## Affected
- Packagist: `mikehaertl/php-shellcommand` — affected >=0 <1.6.1

## Details
php-shellcommand versions before 1.6.1 have a command injection vulnerability. Successful exploitation could lead to arbitrary code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10774
- https://github.com/mikehaertl/php-shellcommand/commit/8d98d8536e05abafe76a491da87296d824939076
- https://github.com/mikehaertl/php-shellcommand
- https://snyk.io/vuln/SNYK-PHP-MIKEHAERTLPHPSHELLCOMMAND-538426
