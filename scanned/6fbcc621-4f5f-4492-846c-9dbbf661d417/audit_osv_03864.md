# [H] ALPINE-CVE-2026-57456

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-57456
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57456
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0699, Vim's Python omni-completion (runtime/autoload/python3complete.vim and the legacy pythoncomplete.vim) executes reconstructed function and class definitions from the current buffer with exec() as part of populating the completion dictionary. When reconstructing that source, each scope's docstring is inserted verbatim between triple quotes with no escaping, so a hostile buffer can break out of the triple-quoted literal and execute attacker-controlled Python during omni-completion. This vulnerability is fixed in 9.2.0699.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57456
