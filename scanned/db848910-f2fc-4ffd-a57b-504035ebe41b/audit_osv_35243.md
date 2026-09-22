# [H] CVE-2025-69906

## Summary
Severity: High
Advisory: CVE-2025-69906
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-05
Source: https://osv.dev/vulnerability/CVE-2025-69906
Type: osv

## Details
Monstra CMS v3.0.4 contains an arbitrary file upload vulnerability in the Files Manager plugin. The application relies on blacklist-based file extension validation and stores uploaded files directly in a web-accessible directory. Under typical server configurations, this can allow an attacker to upload files that are interpreted as executable code, resulting in remote code execution.

## References
- https://github.com/monstra-cms/monstra/tree/master/plugins/box/filesmanager
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69906
- https://github.com/cypherdavy/CVE-2025-69906-Monstra-CMS-3.0.4-Arbitrary-File-Upload-to-RCE
