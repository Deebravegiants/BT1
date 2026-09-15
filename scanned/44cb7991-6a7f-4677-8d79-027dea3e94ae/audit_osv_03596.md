# [H] ALPINE-CVE-2026-33412

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-33412
Ecosystem: Alpine:v3.23
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-33412
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0219-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0202, a command injection vulnerability exists in Vim's glob() function on Unix-like systems. By including a newline character (\n) in a pattern passed to glob(), an attacker may be able to execute arbitrary shell commands. This vulnerability depends on the user's 'shell' setting. This issue has been patched in version 9.2.0202.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-33412
