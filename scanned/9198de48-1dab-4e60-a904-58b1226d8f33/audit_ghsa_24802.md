# [H] SiteServer CMS RCE via unsafe file upload

## Summary
Severity: High
Advisory: GHSA-ff4w-8chr-w2x9
CVE: CVE-2019-11401
CWE: CWE-434
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-ff4w-8chr-w2x9
Type: github-advisory

## Affected
- NuGet: `sscms` — affected >=0 <6.12

## Details
A issue was discovered in SiteServer CMS prior to version 6.12. It allows remote attackers to execute arbitrary code because an administrator can add the permitted file extension `.aassp`, which is converted to `.asp` because the "as" substring is deleted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11401
- https://github.com/siteserver/cms/issues/1858
- https://github.com/siteserver/cms/commit/a7edb9ce3f9b52be3d18fa8a0e44931264e22436#diff-c8a06aaffb97eb2f4c587c1786906edd49dea574d063f74a59d9653ee0d5718b
- https://github.com/siteserver/cms
