# [M] ALPINE-CVE-2026-28419

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-28419
Ecosystem: Alpine:v3.23
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28419
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0078-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0075, a heap-based buffer underflow exists in Vim's Emacs-style tags file parsing logic. When processing a malformed tags file where a delimiter appears at the start of a line, Vim attempts to read memory immediately preceding the allocated buffer. Version 9.2.0075 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28419
