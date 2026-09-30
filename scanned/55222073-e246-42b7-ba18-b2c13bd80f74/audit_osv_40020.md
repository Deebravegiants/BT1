# [H] CVE-2026-48929

## Summary
Severity: High
Advisory: CVE-2026-48929
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48929
Type: osv

## Details
Rocket.Chat in versions <8.5.1, <8.4.4, <8.3.6, <8.2.6, <8.1.6, <8.0.7, <7.13.9, and <7.10.13 is vulnerable to unauthenticated file deletion. The deleteFileMessage Meteor method permanently deletes any uploaded file by ID without requiring authentication. When called via an unauthenticated DDP WebSocket connection, Meteor.userId() returns null, causing the authorization check to be skipped. Execution falls through to FileUpload.getStore('Uploads').deleteById(fileID), which removes the file from storage and database unconditionally. File IDs are discoverable from public channel message payloads and download URLs.

## References
- https://github.com/RocketChat/Rocket.Chat/pull/40889/
- https://hackerone.com/reports/3611837
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48929.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48929
