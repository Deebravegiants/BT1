# [C] ALPINE-CVE-2026-73077

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73077
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73077
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0839, the runtime/ftplugin/sh.vim, runtime/ftplugin/zsh.vim, and runtime/ftplugin/ps1.vim filetype plugins pass attacker-controlled Visual-mode selections from K through keywordprg commands without safely separating shell arguments. fnameescape() and PATH_ESC_CHARS do not neutralize shell metacharacters before ShKeywordPrg, ZshKeywordPrg, or GetHelp invokes bash, zsh, or PowerShell, allowing arbitrary operating-system commands to execute with the privileges of the user running Vim. This issue is fixed in version 9.2.0839.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73077
