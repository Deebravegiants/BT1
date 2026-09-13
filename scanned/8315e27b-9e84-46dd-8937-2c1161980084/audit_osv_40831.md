# [C] Vim: Out-of-bounds Write in Spell File Word Count

## Summary
Severity: Critical
Advisory: CVE-2026-55693
Aliases: GHSA-wgh4-64f7-q3jq
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-55693
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0653, the tree_count_words() function in src/spellfile.c fills in the word-count fields of a spell-file word trie by walking it iteratively with a depth counter. The counter is bounded only by the trie structure itself; it is never checked against the size of the fixed MAXWLEN-element stack arrays it indexes (arridx[], curi[], wordcount[]). A crafted .spl/.sug file pair, loaded when the user invokes spell suggestion, can drive the descent arbitrarily deep, so the function writes past the end of those arrays. This is a stack out-of-bounds write that corrupts the call frame and crashes the editor. This vulnerability is fixed in 9.2.0653.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0653
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55693.json
- https://github.com/vim/vim/security/advisories/GHSA-wgh4-64f7-q3jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-55693
- https://github.com/vim/vim/commit/a80874d9b84a01040e3d1aef2d4a59e1934dafb7
