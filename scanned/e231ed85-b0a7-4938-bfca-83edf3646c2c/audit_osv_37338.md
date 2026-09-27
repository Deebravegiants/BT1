# [C] CVE-2026-31216

## Summary
Severity: Critical
Advisory: CVE-2026-31216
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-31216
Type: osv

## Details
The nexent v1.7.5.2 backend service contains an unauthorized arbitrary storage file deletion vulnerability in its file management API. The DELETE /storage/{object_name:path} endpoint lacks authentication, authorization, and input validation mechanisms. Unauthenticated remote attackers can send crafted requests with a user-controlled object_name path parameter to delete arbitrary files from the underlying MinIO storage system. Successful exploitation leads to data loss and denial of service.

## References
- https://www.notion.so/CVE-2026-31216-35d1e139318881208297f0fbd8005f68
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31216
- https://github.com/ModelEngine-Group/nexent
