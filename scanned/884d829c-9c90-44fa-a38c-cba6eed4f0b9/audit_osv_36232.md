# [C] Open eClass has Unrestricted File Upload that Leads to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: CVE-2026-22241
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/CVE-2026-22241
Type: osv

## Details
The Open eClass platform (formerly known as GUnet eClass) is a complete course management system. Prior to version 4.2, an arbitrary file upload vulnerability in the theme import functionality enables an attacker with administrative privileges to upload arbitrary files on the server's file system. The main cause of the issue is that no validation or sanitization of the file's present inside the zip archive. This leads to remote code execution on the web server. Version 4.2 patches the issue.

## References
- https://twelvesec.com/2026/01/16/rce-via-arbitrary-file-upload-at-open-eclass/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22241.json
- https://github.com/gunet/openeclass/security/advisories/GHSA-gq72-7mwg-424r
- https://github.com/gunet/openeclass/security/advisories/GHSA-rf6j-xgqp-wjxg
- https://nvd.nist.gov/vuln/detail/CVE-2026-22241
- https://github.com/gunet/openeclass/commit/3f9d267b79812a4dd708bb1302339e6a5abe67d9
