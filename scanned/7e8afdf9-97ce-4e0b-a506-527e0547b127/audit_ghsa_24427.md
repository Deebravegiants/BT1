# [C] Craft CMS possibility of brute force attempts

## Summary
Severity: Critical
Advisory: GHSA-wvr4-w6cw-4px8
CVE: CVE-2019-15929
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wvr4-w6cw-4px8
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0 <3.1.7

## Details
In Craft CMS before 3.1.7, the elevated session password prompt was not being rate limited like normal login forms, leading to the possibility of a brute force attempt on them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15929
- https://github.com/craftcms/cms/blob/3.1.7/CHANGELOG-v3.md
