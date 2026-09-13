# [H] RustDesk Server Controls All Handshake Entropy (Salt/Challenge), Enabling Offline Brute-Force

## Summary
Severity: High
Advisory: CVE-2026-30790
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-30790
Type: osv

## Details
Improper Restriction of Excessive Authentication Attempts, Use of Password Hash With Insufficient Computational Effort vulnerability in rustdesk-server-pro RustDesk Server Pro rustdesk-server-pro on Windows, MacOS, Linux (Peer authentication, API login modules), rustdesk-server RustDesk Server (OSS) rustdesk-server on Windows, MacOS, Linux (Peer authentication, API login modules) allows Password Brute Forcing. This vulnerability is associated with program files src/server/connection.Rs and program routines Salt/challenge generation, SHA256(SHA256(pwd+salt)+challenge) verification.

This issue affects RustDesk Server Pro: through 1.7.5; RustDesk Server (OSS): through 1.1.15.

## References
- https://github.com/rustdesk
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30790.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-30790
- https://www.vulsec.org/
- https://github.com/rustdesk/rustdesk-server
- https://github.com/rustdesk/rustdesk-server-pro/releases
- https://github.com/rustdesk/rustdesk-server/releases
- https://docs.google.com/document/d/e/2PACX-1vSds6jjpd38oO_yIAyd1HYtKNUuea-I-ozAPpGhYI7QgAU-QGJ7D8a4rOZVj1vmiUXV1EcdRHf9aZAW/pub
