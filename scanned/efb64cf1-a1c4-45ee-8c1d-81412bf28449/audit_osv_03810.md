# [H] ALPINE-CVE-2026-52860

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-52860
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-52860
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0602-r0

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0597, Vim's Python omni-completion executes reconstructed function and class definitions from the current buffer with exec() as part of populating the completion dictionary. Python evaluates function default values, parameter annotations, and class base expressions at definition time, so a hostile buffer can execute attacker-controlled Python expressions during omni-completion. The existing g:pythoncomplete_allow_import mitigation (GHSA-52mc-rq6p-rc7c) does not cover this path, because the attacker-controlled code is not a harvested import/from statement. This issue has been patched in version 9.2.0597.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-52860
