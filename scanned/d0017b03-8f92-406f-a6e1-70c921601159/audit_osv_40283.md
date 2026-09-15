# [H] Wekan: Arbitrary file read and server DoS via attachment versions.original.path

## Summary
Severity: High
Advisory: CVE-2026-52890
Aliases: GHSA-g6vm-7757-pr88
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-52890
Type: osv

## Details
Wekan is open source kanban built with Meteor. Prior to 9.31, Wekan allows a logged-in board member to insert an attachment document through the /attachments/insert DDP method with attacker-controlled versions.original.path and versions.original.storage fields. The server/permissions/attachments.js insert rule checks only board write access, and FileStoreStrategyFilesystem.getReadStream() in models/lib/fileStoreStrategy.js streams the stored path without a storage-root containment check, allowing arbitrary file reads and denial of service through special files such as /dev/zero. This issue is fixed in version 9.31.

## References
- https://github.com/wekan/wekan/releases/tag/v9.31
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52890.json
- https://github.com/wekan/wekan/security/advisories/GHSA-g6vm-7757-pr88
- https://nvd.nist.gov/vuln/detail/CVE-2026-52890
- https://github.com/wekan/wekan/commit/fc92b342ceedcf38dbd614a0f7b50d6dc2b22eb8
