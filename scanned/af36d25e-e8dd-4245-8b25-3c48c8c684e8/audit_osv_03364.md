# [M] ALPINE-CVE-2025-61915

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-61915
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-61915
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.16-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. Prior to version 2.4.15, a user in the lpadmin group can use the cups web ui to change the config and insert a malicious line. Then the cupsd process which runs as root will parse the new config and cause an out-of-bound write. This issue has been patched in version 2.4.15.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-61915
