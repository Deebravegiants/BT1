# [M] ALPINE-CVE-2026-73070

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-73070
Ecosystem: Alpine:v3.23
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73070
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0842, the socket server backend in src/socketserver.c accepts unbounded client connections in socketserver_accept(), causing descriptors to overflow fd_set structures in src/channel.c and fixed-size struct pollfd arrays in src/os_unix.c, which allows a local process that can connect to the server socket to corrupt stack memory or terminate the Vim server. This issue is fixed in version 9.2.0842.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73070
