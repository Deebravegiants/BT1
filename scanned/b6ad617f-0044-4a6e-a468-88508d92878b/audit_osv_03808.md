# [H] ALPINE-CVE-2026-52858

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-52858
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-52858
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0498-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0561, the Python omni-completion script in python3complete.vim for Vim with the +python3 interpreter enabled (and the legacy pythoncomplete.vim for builds with the +python interpreter) executes the import and from statements found in the current buffer through Python's import machinery. Because the buffer's working directory is on sys.path, opening a hostile .py file with a sibling Python package and invoking omni-completion runs that package's top-level code as the editing user. This issue has been patched in version 9.2.0561.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-52858
