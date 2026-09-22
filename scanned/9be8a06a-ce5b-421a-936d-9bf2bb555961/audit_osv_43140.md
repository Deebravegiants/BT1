# [H] Cockpit CMS Cockpit CMS - Unrestricted File Upload

## Summary
Severity: High
Advisory: CVE-2026-72557
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72557
Type: osv

## Details
An unrestricted file upload vulnerability in Cockpit CMS 2.6.0 allows authenticated users to upload files of any extension including PHP scripts via the asset upload endpoint. The allowed_uploads configuration defaults to wildcard (*) and uploaded files are stored in a web-accessible directory. An attacker with any authenticated account can upload a PHP webshell and execute arbitrary OS commands on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72557.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72557
- https://github.com/Cockpit-HQ/Cockpit
