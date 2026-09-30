# [C] RomM's authenticated arbitrary file write vulnerability can lead to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-54071
Aliases: GHSA-fgxf-hggc-qqmq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-07-21
Source: https://osv.dev/vulnerability/CVE-2025-54071
Type: osv

## Details
RomM (ROM Manager) allows users to scan, enrich, browse and play their game collections with a clean and responsive interface. In versions 4.0.0-beta.3 and below, an authenticated arbitrary file write vulnerability exists in the /api/saves endpoint. This can lead to Remote Code Execution on the system. The vulnerability permits arbitrary file write operations, allowing attackers to create or modify files at any filesystem location with user-supplied content. A user with viewer role or Scope.ASSETS_WRITE permission or above is required to pass authentication checks. The vulnerability is fixed in version 4.0.0-beta.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54071.json
- https://github.com/rommapp/romm/security/advisories/GHSA-fgxf-hggc-qqmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-54071
- https://github.com/rommapp/romm/commit/89248d03805e5fabca78443dd202ff32e0b4d9f3
