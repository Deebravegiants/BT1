# [H] 4ga Boards: Import Path Traversal Leads to Arbitrary File Read

## Summary
Severity: High
Advisory: CVE-2026-41419
Aliases: GHSA-rrjq-7x8g-cmgm
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41419
Type: osv

## Details
4ga Boards is a boards system for realtime project management. Prior to 3.3.5, a path traversal vulnerability allows an authenticated user with board import privileges to make the server ingest arbitrary host files as board attachments during BOARDS archive import. Once imported, the file can be downloaded through the normal application interface, resulting in unauthorized local file disclosure. This vulnerability is fixed in 3.3.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41419.json
- https://github.com/RARgames/4gaBoards/security/advisories/GHSA-rrjq-7x8g-cmgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-41419
