# [C] ALPINE-CVE-2026-73078

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73078
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73078
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0840, runtime/plugin/netrwPlugin.vim loads netrw and runtime/pack/dist/opt/netrw/autoload/netrw.vim constructs Bookmarks, History, and Targets menu entries by interpolating attacker-controlled directory paths into executed :menu commands. s:NetrwBookmarkMenu(), s:NetrwTgtMenu(), g:netrw_menu_escape, EX_TRLBAR, and netrw#MakeTgt() fail to neutralize the | command separator or single quotes at five construction sites, allowing a crafted path browsed or bookmarked in GUI Vim to execute arbitrary Ex and operating-system commands. This issue is fixed in version 9.2.0840.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73078
