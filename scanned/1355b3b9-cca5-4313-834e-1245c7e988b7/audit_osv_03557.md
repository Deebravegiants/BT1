# [H] ALPINE-CVE-2026-28421

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28421
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28421
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0078-r0

## Details
Vim is an open source, command line text editor. Versions prior to 9.2.0077 have a heap-buffer-overflow and a segmentation fault (SEGV) exist in Vim's swap file recovery logic. Both are caused by unvalidated fields read from crafted pointer blocks within a swap file. Version 9.2.0077 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28421
