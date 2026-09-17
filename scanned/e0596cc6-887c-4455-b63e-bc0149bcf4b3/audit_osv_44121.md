# [C] Low-privilege RCE through element-search eager loading

## Summary
Severity: Critical
Advisory: CVE-2026-79987
Aliases: GHSA-9c4j-cjw3-r3xx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-79987
Type: osv

## Details
A remote, authenticated, non-admin Craft CMS Control Panel user with only the accessCp permission can execute operating system commands as the PHP web worker.

## References
- https://packagist.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79987.json
- https://github.com/craftcms/cms/releases/tag/5.10.13
- https://github.com/craftcms/cms/security/advisories/GHSA-9c4j-cjw3-r3xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-79987
- https://www.hckrt.com/hacktivity/HCKRT-9TSYY2
- https://github.com/craftcms/cms
