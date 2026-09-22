# [M] RustDesk hbbs/hbbr Servers Broker Connections Without Any Authorization Check

## Summary
Severity: Medium
Advisory: CVE-2026-30784
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30784
Type: osv

## Details
Missing Authorization, Missing Authentication for Critical Function vulnerability in rustdesk-server RustDesk Server rustdesk-server, rustdesk-server-pro on hbbs/hbbr on all server platforms (Rendezvous server (hbbs), relay server (hbbr) modules) allows Privilege Abuse. This vulnerability is associated with program files src/rendezvous_server.Rs, src/relay_server.Rs and program routines handle_punch_hole_request(), RegisterPeer handler, relay forwarding.

This issue affects RustDesk Server: through 1.7.5, through 1.1.15.

## References
- https://github.com/rustdesk/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30784.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30784
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk-server
- https://rustdesk.com/docs/en/self-host/
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
