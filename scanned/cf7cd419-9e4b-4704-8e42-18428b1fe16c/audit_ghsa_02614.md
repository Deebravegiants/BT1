# [C] Unrestricted File Upload in ShowDoc v2.9.5

## Summary
Severity: Critical
Advisory: GHSA-c442-3278-rhrg
CVE: CVE-2021-36440
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-09
Source: https://github.com/advisories/GHSA-c442-3278-rhrg
Type: github-advisory

## Affected
- Packagist: `showdoc/showdoc` — affected >=0 <2.9.6

## Details
Unrestricted File Upload in ShowDoc v2.9.5 allows remote attackers to execute arbitrary code via the 'file_url' parameter in the component AdminUpdateController.class.php'.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36440
- https://github.com/star7th/showdoc/issues/1406
- https://github.com/star7th/showdoc/commit/49b992d4c548c8c615a92b6efe8a50c8f1083abf
- https://github.com/star7th/showdoc
