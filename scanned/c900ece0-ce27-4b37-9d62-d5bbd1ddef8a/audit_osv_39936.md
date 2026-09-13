# [C] CVE-2026-48616

## Summary
Severity: Critical
Advisory: CVE-2026-48616
CVSS: 9.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-48616
Type: osv

## Details
Rocket.Chat versions <8.5.1, 8.4.4, 8.3.6, 8.2.6, 8.1.6, 8.0.7, 7.13.9, 7.10.13 has an access control vulnerability in Livechat files. Protected file downloads at /file-upload/:fileId/:name authorize livechat access using rc_room_type=l with rc_rid+rc_token, but the authorization path does not verify that rc_rid matches the requested file's rid. Furthermore, :fileId is predictable via sequential MongoDB IDs, and :name can be anything, allowing unauthenticated discovery of all uploaded files.

## References
- https://hackerone.com/reports/3687142
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-48616
- https://github.com/RocketChat/Rocket.Chat/pull/40889
