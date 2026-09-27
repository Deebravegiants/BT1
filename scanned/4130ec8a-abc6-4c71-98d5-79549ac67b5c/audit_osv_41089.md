# [C] Vim: Stack out-of-bounds write in `spell_soundfold_sofo()` via an over-length `soundfold()` argument

## Summary
Severity: Critical
Advisory: CVE-2026-57455
Aliases: GHSA-q8mh-6qm3-25g4
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57455
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0698, the single-byte branch of spell_soundfold_sofo() in src/spell.c translates a word through a spell file's SOFO (sound-folding) byte map into a caller-owned result buffer. Its copy loop advances the output index ri with no upper bound and terminates only on the input NUL, writing one byte per input byte into the MAXWLEN-element stack buffer the caller provides. A word longer than MAXWLEN, passed to soundfold() (or reached via sound-based spell suggestion) while a SOFO-based spell language is active, therefore writes past the end of that buffer. This is a stack out-of-bounds write that corrupts the call frame and crashes the editor. This vulnerability is fixed in 9.2.0698.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0698
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57455.json
- https://github.com/vim/vim/security/advisories/GHSA-q8mh-6qm3-25g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-57455
- https://github.com/vim/vim/commit/497f931f85339d175d7f69588dd249e8ccfed41b
