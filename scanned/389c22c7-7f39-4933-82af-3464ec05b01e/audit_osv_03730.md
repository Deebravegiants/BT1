# [H] ALPINE-CVE-2026-43961

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-43961
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43961
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0481-r0

## Details
A flaw was found in Vim's netrw plugin. A crafted filename containing quote characters and expression fragments can break out of the quoted context during mark/unmark operations, allowing arbitrary Vimscript execution. This can be leveraged to run shell commands with the privileges of the user running Vim.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43961
