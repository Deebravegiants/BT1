# [H] Improper Input Validation in danny-avila/librechat

## Summary
Severity: High
Advisory: CVE-2024-11171
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11171
Type: osv

## Details
In danny-avila/librechat version git 0c2a583, there is an improper input validation vulnerability. The application uses multer middleware for handling multipart file uploads. When using in-memory storage (the default setting for multer), there is no limit on the upload file size. This can lead to a server crash due to out-of-memory errors when handling large files. An attacker without any privileges can exploit this vulnerability to cause a complete denial of service. The issue is fixed in version 0.7.6.

## References
- https://huntr.com/bounties/91717a5a-d653-4e35-b186-9e8d00aa4285
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11171.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11171
- https://github.com/danny-avila/librechat/commit/bb58a2d0662ef86dc75a9d2f6560125c018e3836
