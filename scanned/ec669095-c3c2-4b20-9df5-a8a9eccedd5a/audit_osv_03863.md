# [H] ALPINE-CVE-2026-57455

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-57455
Ecosystem: Alpine:v3.23
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57455
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0698, the single-byte branch of spell_soundfold_sofo() in src/spell.c translates a word through a spell file's SOFO (sound-folding) byte map into a caller-owned result buffer. Its copy loop advances the output index ri with no upper bound and terminates only on the input NUL, writing one byte per input byte into the MAXWLEN-element stack buffer the caller provides. A word longer than MAXWLEN, passed to soundfold() (or reached via sound-based spell suggestion) while a SOFO-based spell language is active, therefore writes past the end of that buffer. This is a stack out-of-bounds write that corrupts the call frame and crashes the editor. This vulnerability is fixed in 9.2.0698.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57455
