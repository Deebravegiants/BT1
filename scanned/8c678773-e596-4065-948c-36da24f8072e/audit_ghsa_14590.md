# [M] Craft CMS Stored Cross-site Scripting Injection Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qcrj-6ffc-v7hq
CVE: CVE-2023-23927
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-qcrj-6ffc-v7hq
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.3.7
- Packagist: `craftcms/cms` — affected >=3.7.24 <3.7.64

## Details
### Summary
_When you insert a payload inside a label name or instruction of an entry type, an XSS happens in the quick post widget on the 
admin dashboard._



### PoC
[_Complete instructions, including specific configuration details, to reproduce the vulnerability._](https://user-images.githubusercontent.com/53917092/215604129-d5b75608-5a24-4eb3-906f-55b192310298.mp4)

### Impact
Tested with the free version of Craft CMS 4.3.6.1

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-qcrj-6ffc-v7hq
- https://nvd.nist.gov/vuln/detail/CVE-2023-23927
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/develop/CHANGELOG.md#437---2023-02-03
- https://user-images.githubusercontent.com/53917092/215604129-d5b75608-5a24-4eb3-906f-55b192310298.mp4
