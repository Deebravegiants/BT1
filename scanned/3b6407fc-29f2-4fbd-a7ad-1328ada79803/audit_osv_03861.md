# [H] ALPINE-CVE-2026-57453

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-57453
Ecosystem: Alpine:v3.23
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57453
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=9.1.1784 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. From 9.1.1784 until 9.2.0678, when the bundled zip plugin autoload/zip.vim falls back to PowerShell to browse, read, extract, update or delete entries in a zip archive, it builds the PowerShell command by inserting archive entry names that are quoted only for the shell, not for PowerShell. A crafted entry name can break out of the intended string context and cause PowerShell to execute arbitrary commands with the privileges of the user running Vim, triggered by opening, viewing or extracting the archive. This vulnerability is fixed in 9.2.0678.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57453
