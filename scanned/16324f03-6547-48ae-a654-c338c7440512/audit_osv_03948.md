# [C] ALPINE-CVE-2026-73073

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73073
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73073
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0845, StructMembers() in runtime/autoload/ccomplete.vim constructs and executes a vimgrep command using an insufficiently escaped typeref: or typename: value from a tags file, allowing an unterminated collection followed by a command separator to execute arbitrary Ex and operating-system commands when a user invokes C omni-completion with CTRL-X CTRL-O on a member access whose type is resolved from that tags file. This issue is fixed in version 9.2.0845.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73073
