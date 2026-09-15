# [M] ALPINE-CVE-2025-58436

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-58436
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58436
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.16-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.16-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. Prior to version 2.4.15, a client that connects to cupsd but sends slow messages, e.g. only one byte per second, delays cupsd as a whole, such that it becomes unusable by other clients. This issue has been patched in version 2.4.15.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58436
