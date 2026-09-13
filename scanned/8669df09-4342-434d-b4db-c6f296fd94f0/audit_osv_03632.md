# [M] ALPINE-CVE-2026-34979

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-34979
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34979
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.18-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, there is a heap-based buffer overflow in the CUPS scheduler when building filter option strings from job attribute. At time of publication, there are no publicly available patches.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34979
