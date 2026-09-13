# [C] Gleez Cms Server Side Request Forgery (SSRF) vulnerability

## Summary
Severity: Critical
Advisory: GHSA-7mxg-r76p-363g
CVE: CVE-2021-27312
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-03
Source: https://github.com/advisories/GHSA-7mxg-r76p-363g
Type: github-advisory

## Affected
- Packagist: `gleez/cms` — affected >=0

## Details
Server Side Request Forgery (SSRF) vulnerability in Gleez Cms 1.2.0, allows remote attackers to execute arbitrary code and obtain sensitive information via modules/gleez/classes/request.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-27312
- https://github.com/gleez/cms/issues/805
- https://gist.github.com/LioTree/8d10d123d31f50db05a25586e62a87ba
- https://github.com/gleez/cms
