# [M] CVE-2025-56869

## Summary
Severity: Medium
Advisory: CVE-2025-56869
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-56869
Type: osv

## Details
Directory traversal vulnerability in Sync In server thru 1.1.1 allowing authenticated attackers to gain read and write access to the system via FilesManager.saveMultipart function in backend/src/applications/files/services/files-manager.service.ts, and FilesManager.compress function in backend/src/applications/files/services/files-manager.service.ts.

## References
- https://github.com/Sync-in/server/releases/tag/v1.2.0
- https://sync-in.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/56xxx/CVE-2025-56869.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-56869
- https://github.com/Sync-in/server
