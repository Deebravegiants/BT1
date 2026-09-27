# [C] Craft CMS 5.0.0-RC1 before 5.10.12 Behavior Injection RCE

## Summary
Severity: Critical
Advisory: CVE-2026-86730
Aliases: GHSA-qj4v-m29p-fj4m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86730
Type: osv

## Details
Craft CMS versions before 5.10.12 fail to properly cleanse string-typed field-layout elements, allowing authenticated control-panel users to inject Yii2 behavior attachments and event handlers. Attackers can post field-layout tab elements as JSON strings to bypass cleanse validation, then trigger arbitrary object instantiation and code execution through Craft::createObject().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86730.json
- https://github.com/craftcms/cms/security/advisories/GHSA-qj4v-m29p-fj4m
- https://nvd.nist.gov/vuln/detail/CVE-2026-86730
- https://www.vulncheck.com/advisories/craft-cms-5.0.0-rc1-before-5.10.12-behavior-injection-rce
