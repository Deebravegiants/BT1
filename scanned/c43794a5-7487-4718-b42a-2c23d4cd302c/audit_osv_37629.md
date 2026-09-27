# [M] NFA regex engine NULL pointer dereference affects Vim < 9.2.0137

## Summary
Severity: Medium
Advisory: CVE-2026-32249
Aliases: GHSA-9phh-423r-778r
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-32249
Type: osv

## Details
Vim is an open source, command line text editor. From 9.1.0011 to before 9.2.0137, Vim's NFA regex compiler, when encountering a collection containing a combining character as the endpoint of a character range (e.g. [0-0\u05bb]), incorrectly emits the composing bytes of that character as separate NFA states. This corrupts the NFA postfix stack, resulting in NFA_START_COLL having a NULL out1 pointer. When nfa_max_width() subsequently traverses the compiled NFA to estimate match width for the look-behind assertion, it dereferences state->out1->out without a NULL check, causing a segmentation fault. This vulnerability is fixed in 9.2.0137.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0137
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32249.json
- https://github.com/vim/vim/security/advisories/GHSA-9phh-423r-778r
- https://nvd.nist.gov/vuln/detail/CVE-2026-32249
- https://github.com/vim/vim/commit/36d6e87542cf823d833e451e09a90ee429899cec
