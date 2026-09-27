# [M] ALPINE-CVE-2026-44656

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-44656
Ecosystem: Alpine:v3.23
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-44656
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0437-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0435, an OS command injection vulnerability exists in Vim's :find command-line completion. When the path option contains backtick-enclosed shell commands, those commands are executed during file name completion. Because the path option lacks the P_SECURE flag, it can be set from a modeline, allowing an attacker who controls the contents of a file to execute arbitrary shell commands when the user opens that file in Vim and triggers :find completion. This issue has been patched in version 9.2.0435.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-44656
