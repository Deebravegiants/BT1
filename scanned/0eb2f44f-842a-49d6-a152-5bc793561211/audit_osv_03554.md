# [M] ALPINE-CVE-2026-28418

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-28418
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28418
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0078-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0074, a heap-based buffer overflow out-of-bounds read exists in Vim's Emacs-style tags file parsing logic. When processing a malformed tags file, Vim can be tricked into reading up to 7 bytes beyond the allocated memory boundary. Version 9.2.0074 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28418
