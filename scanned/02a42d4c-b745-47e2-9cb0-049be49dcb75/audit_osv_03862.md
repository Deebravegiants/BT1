# [M] ALPINE-CVE-2026-57454

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-57454
Ecosystem: Alpine:v3.23
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57454
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=9.2.0320 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. From 9.2.0320 until 9.2.0679, a crafted undo or swap file can store a virtual-text property whose offset and length point outside the line's property data. When Vim restores or displays such a line it converts the offset into a pointer and reads the virtual text without bounds checking, causing an out-of-bounds read that can crash Vim or disclose adjacent heap memory. This vulnerability is fixed in 9.2.0679.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57454
