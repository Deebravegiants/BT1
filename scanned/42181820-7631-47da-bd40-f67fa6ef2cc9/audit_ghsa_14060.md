# [M] Stored cross site scripting in Craft CMS

## Summary
Severity: Medium
Advisory: GHSA-7x94-jx75-3gh6
CVE: CVE-2023-2817
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-7x94-jx75-3gh6
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.4.12

## Details
A post-authentication stored cross-site scripting vulnerability exists in Craft CMS versions <= 4.4.11. HTML, including script tags can be injected into field names which, when the field is added to a category or section, will trigger when users visit the Categories or Entries pages respectively. This issue was patched in version 4.4.12.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2817
- https://github.com/craftcms/cms/commit/7655e1009ba6cdbfb230e6bb138b775b69fc7bcb
- https://github.com/craftcms/cms
- https://www.tenable.com/security/research/tra-2023-20
