# [H] ALPINE-CVE-2025-27423

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-27423
Ecosystem: Alpine:v3.22, Alpine:v3.23
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-27423
Type: osv

## Affected
- Alpine:v3.22: `vim` — affected >=9.1.0858 <9.1.1164-r0
- Alpine:v3.23: `vim` — affected >=9.1.0858 <9.1.1164-r0

## Details
Vim is an open source, command line text editor. Vim is distributed with the tar.vim plugin, that allows easy editing and viewing of (compressed or uncompressed) tar files. Starting with 9.1.0858, the tar.vim plugin uses the ":read" ex command line to append below the cursor position, however the is not sanitized and is taken literally from the tar archive. This allows to execute shell commands via special crafted tar archives. Whether this really happens, depends on the shell being used ('shell' option, which is set using $SHELL). The issue has been fixed as of Vim patch v9.1.1164

## References
- https://security.alpinelinux.org/vuln/CVE-2025-27423
