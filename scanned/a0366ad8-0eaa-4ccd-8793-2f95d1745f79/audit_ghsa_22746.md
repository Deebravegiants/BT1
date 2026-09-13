# [C] ThinkPHP SQL injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-75fm-52mm-q5rm
CVE: CVE-2018-17566
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-75fm-52mm-q5rm
Type: github-advisory

## Affected
- Packagist: `topthink/framework` — affected 5.1.24

## Details
In ThinkPHP 5.1.24, the inner function delete can be used for SQL injection when its WHERE condition's value can be controlled by a user's request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-17566
- https://github.com/top-think/think/issues/858
- https://github.com/top-think/framework
