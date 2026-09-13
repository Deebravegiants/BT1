# [H] ALPINE-CVE-2026-34982

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34982
Ecosystem: Alpine:v3.23
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34982
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0280-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0276, a modeline sandbox bypass in Vim allows arbitrary OS command execution when a user opens a crafted file. The `complete`, `guitabtooltip` and `printheader` options are missing the `P_MLE` flag, allowing a modeline to be executed. Additionally, the `mapset()` function lacks a `check_secure()` call, allowing it to be abused from sandboxed expressions. Commit 9.2.0276 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34982
