# [M] ALPINE-CVE-2026-55892

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-55892
Ecosystem: Alpine:v3.23
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-55892
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0662, the dump_prefixes() function in src/spell.c walks a spell-file prefix trie iteratively with a depth counter while dumping the prefixes that apply to a word. The counter is bounded only by the trie structure itself; it is never checked against the size of the fixed MAXWLEN-element stack arrays it indexes (prefix[], arridx[], curi[]). A crafted .spl file, loaded when the user dumps the word list, can drive the descent arbitrarily deep, so the function writes past the end of those arrays. This is a stack out-of-bounds write that corrupts the call frame and crashes the editor. This vulnerability is fixed in 9.2.0662.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-55892
