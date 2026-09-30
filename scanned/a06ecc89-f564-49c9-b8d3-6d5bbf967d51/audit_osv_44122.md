# [C] Authenticated RCE through Twig sandbox escape

## Summary
Severity: Critical
Advisory: CVE-2026-79988
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-79988
Type: osv

## Details
The Twig sandbox mechanism in Craft CMS is configured to allow dangerous functionality from the Yii framework, leading to authenticated RCE similar to previously disclosed vulnerabilities.

## References
- https://packagist.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79988.json
- https://github.com/craftcms/cms/releases/tag/5.10.7
- https://nvd.nist.gov/vuln/detail/CVE-2026-79988
- https://www.hckrt.com/hacktivity/HCKRT-8RQQ7K
- https://github.com/craftcms/cms
