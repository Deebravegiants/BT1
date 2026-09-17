# [H] ALPINE-CVE-2026-28417

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28417
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28417
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0078-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0073, an OS command injection vulnerability exists in the `netrw` standard plugin bundled with Vim. By inducing a user to open a crafted URL (e.g., using the `scp://` protocol handler), an attacker can execute arbitrary shell commands with the privileges of the Vim process. Version 9.2.0073 fixes the issue.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28417
