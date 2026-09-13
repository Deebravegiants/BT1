# [C] MyTube has an Improper Access Control that Allows Complete Application Takeover

## Summary
Severity: Critical
Advisory: CVE-2026-33735
Aliases: GHSA-63cf-662x-crp2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33735
Type: osv

## Details
MyTube is a self-hosted downloader and player for several video websites Prior to version 1.8.69, an authorization bypass in the `/api/settings/import-database` endpoint allows attackers with low-privilege credentials to upload and replace the application's SQLite database entirely, leading to a full compromise of the application. The bypass is relevant for other POST routes as well. Version 1.8.69 fixes the issue.

## References
- https://github.com/franklioxygen/MyTube/blob/6ade838a46366174e2c030f856340f3856e03132/backend/src/middleware/roleBasedSettingsMiddleware.ts#L116
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33735.json
- https://github.com/franklioxygen/MyTube/security/advisories/GHSA-63cf-662x-crp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33735
- https://github.com/franklioxygen/MyTube/commit/b7bf9b7960958c6c51f85fe50a2fc041a086c466
