# [H] ALPINE-CVE-2026-35177

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-35177
Ecosystem: Alpine:v3.23
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-35177
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0280-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0280, a path traversal bypass in Vim's zip.vim plugin allows overwriting of arbitrary files when opening specially crafted zip archives, circumventing the previous fix for CVE-2025-53906. This vulnerability is fixed in 9.2.0280.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-35177
