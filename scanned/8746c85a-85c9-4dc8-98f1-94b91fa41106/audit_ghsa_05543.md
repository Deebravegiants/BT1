# [M] Craft CMS vulnerable to potential information disclosure via unchecked asset relocation

## Summary
Severity: Medium
Advisory: GHSA-53vf-c43h-j2x9
CVE: CVE-2025-68436
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-53vf-c43h-j2x9
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.21
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.17

## Details
Authenticated users on a Craft installation could potentially expose sensitive assets via their user profile photo via maliciously crafted requests.

Users should update to the patched versions (5.8.21 and 4.16.17) to mitigate the issue.

Resources:

https://github.com/craftcms/cms/commit/4bcb0db554e273b66ce3b75263a13414c2368fc9

https://github.com/craftcms/cms/commit/4bcb0db554e273b66ce3b75263a13414c2368fc9

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-53vf-c43h-j2x9
- https://nvd.nist.gov/vuln/detail/CVE-2025-68436
- https://github.com/craftcms/cms/commit/4bcb0db554e273b66ce3b75263a13414c2368fc9
- https://github.com/craftcms/cms
