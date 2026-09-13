# [M] CVE-2026-29909

## Summary
Severity: Medium
Advisory: CVE-2026-29909
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-29909
Type: osv

## Details
MRCMS V3.1.2 contains an unauthenticated directory enumeration vulnerability in the file management module. The /admin/file/list.do endpoint lacks authentication controls and proper input validation, allowing remote attackers to enumerate directory contents on the server without any credentials.

## References
- https://github.com/qflksheep/CVE-2026-29909-MRCMS-vulnerability/blob/main/README.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29909.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-29909
- https://github.com/wuweiit/mushroom
