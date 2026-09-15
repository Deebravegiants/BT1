# [M] ALPINE-CVE-2026-41411

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-41411
Ecosystem: Alpine:v3.23
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-41411
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0357-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0357, A command injection vulnerability exists in Vim's tag file processing. When resolving a tag, the filename field from the tags file is passed through wildcard expansion to resolve environment variables and wildcards. If the filename field contains backtick syntax (e.g., `command`), Vim executes the embedded command via the system shell with the full privileges of the running user.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-41411
