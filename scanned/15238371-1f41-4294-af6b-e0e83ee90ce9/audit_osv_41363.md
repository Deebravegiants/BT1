# [H] Hoppscotch: Insecure Default Configuration Allows Public Exposure of Private Collection Data via Mock Server

## Summary
Severity: High
Advisory: CVE-2026-59720
Aliases: GHSA-c68f-wr5p-j6jf
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59720
Type: osv

## Details
Hoppscotch is an open source API development ecosystem. Prior to 2026.6.0, mock server creation in mock-server.service.ts does not persist the isPublic input field while schema.prisma defaults isPublic to true, causing mock servers linked to private collections to be publicly accessible without authentication and potentially expose sensitive API data. This issue is fixed in version 2026.6.0.

## References
- https://github.com/hoppscotch/hoppscotch/releases/tag/2026.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59720.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-c68f-wr5p-j6jf
- https://nvd.nist.gov/vuln/detail/CVE-2026-59720
- https://github.com/hoppscotch/hoppscotch/commit/e4332110d455a3012d5c77a9186bc4aa096e34f2
- https://github.com/hoppscotch/hoppscotch/pull/6410
