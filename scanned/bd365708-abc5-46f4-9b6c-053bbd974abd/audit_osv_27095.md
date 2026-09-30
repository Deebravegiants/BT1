# [H] Arbitrary File Deletion via Path Traversal in danny-avila/librechat

## Summary
Severity: High
Advisory: CVE-2024-10361
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10361
Type: osv

## Details
An arbitrary file deletion vulnerability exists in danny-avila/librechat version v0.7.5-rc2, specifically within the /api/files endpoint. This vulnerability arises from improper input validation, allowing path traversal techniques to delete arbitrary files on the server. Attackers can exploit this to bypass security mechanisms and delete files outside the intended directory, including critical system files, user data, or application resources. This vulnerability impacts the integrity and availability of the system.

## References
- https://huntr.com/bounties/e811f7f7-9556-4564-82e2-5b3d17599b2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10361.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10361
- https://github.com/danny-avila/librechat/commit/0b744db1e2af31a531ffb761584d85540430639c
