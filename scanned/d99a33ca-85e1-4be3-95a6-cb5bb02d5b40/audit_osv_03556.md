# [M] ALPINE-CVE-2026-28420

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-28420
Ecosystem: Alpine:v3.23
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28420
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0078-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0076, a heap-based buffer overflow WRITE and an out-of-bounds READ exist in Vim's terminal emulator when processing maximum combining characters from Unicode supplementary planes. Version 9.2.0076 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28420
