# [M] Onyx: IDOR in /chat/file/{file_id} allows any authenticated user to download other users files

## Summary
Severity: Medium
Advisory: CVE-2026-42277
Aliases: GHSA-vg3h-35f7-7w6r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42277
Type: osv

## Details
Onyx is an open-source AI platform. Prior to versions 3.0.9, 3.1.6, and 3.2.6, the GET /chat/file/{file_id} endpoint allows any authenticated user to download any other user's uploaded files by providing the file UUID. The endpoint verifies the caller is authenticated but never checks that the file belongs to them. An attacker who knows or obtains a file UUID can access confidential documents, chat attachments, and other files uploaded by any user in the system. This issue has been patched in versions 3.0.9, 3.1.6, and 3.2.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42277.json
- https://github.com/onyx-dot-app/onyx/security/advisories/GHSA-vg3h-35f7-7w6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42277
