# [M] ALPINE-CVE-2026-42307

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42307
Ecosystem: Alpine:v3.23
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42307
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0389-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0383, an OS command injection vulnerability exists in the netrw standard plugin bundled with Vim. By inducing a user to open a crafted URL (e.g., using the sftp:// or file:// protocol handlers), an attacker can execute arbitrary shell commands with the privileges of the Vim process. This issue has been patched in version 9.2.0383.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42307
