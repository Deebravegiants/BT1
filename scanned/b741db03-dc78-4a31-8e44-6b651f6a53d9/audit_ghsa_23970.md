# [H] Craft CMS PHP Code Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-r342-vjc4-wrmj
CVE: CVE-2018-3814
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r342-vjc4-wrmj
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=0

## Details
Craft CMS 2.6.3000 allows remote attackers to execute arbitrary PHP code by using the "Assets->Upload files" screen and then the "Replace it" option, because this allows a .jpg file to have embedded PHP code, and then be renamed to a .php extension.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3814
- https://github.com/Snowty/myCVE/blob/master/CraftCMS-2.6.3000/README.md
- https://github.com/craftcms/cms
- https://web.archive.org/web/20170612231205/http://0day5.com/archives/4122
