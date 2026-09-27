# [C] Brave CMS has Unrestricted File Upload in BraveCMS via CKEditor Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-35047
Aliases: GHSA-9rcc-w59j-965v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-35047
Type: osv

## Details
Brave CMS is an open-source CMS. Prior to 2.0.6, an Unrestricted File Upload vulnerability in the CKEditor endpoint allows attackers to upload arbitrary files, including executable scripts. This may lead to Remote Code Execution (RCE) on the server, potentially resulting in full system compromise, data exfiltration, or service disruption. All users running affected versions of BraveCMS are impacted. This vulnerability is fixed in 2.0.6.

## References
- https://github.com/Ajax30/BraveCMS-2.0/security/advisories/GHSA-9rcc-w59j-965v
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35047.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-35047
- https://github.com/Ajax30/BraveCMS-2.0/commit/058ee4ed7c2b39d540af8274024afcbc9532aa83
- https://github.com/Ajax30/BraveCMS-2.0/pull/122
