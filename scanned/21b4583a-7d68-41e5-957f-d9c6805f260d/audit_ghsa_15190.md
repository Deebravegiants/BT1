# [M] juzawebCMS Incorrect Access Control vulnerability

## Summary
Severity: Medium
Advisory: GHSA-93p6-9cxv-5rpq
CVE: CVE-2023-46906
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-09
Source: https://github.com/advisories/GHSA-93p6-9cxv-5rpq
Type: github-advisory

## Affected
- Packagist: `juzaweb/cms` — affected >=0

## Details
juzaweb <= 3.4 is vulnerable to Incorrect Access Control, resulting in an application outage after a 500 HTTP status code. The payload in the timezone field was not correctly validated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46906
- https://github.com/juzaweb/cms
- https://www.sumor.top/index.php/archives/880
