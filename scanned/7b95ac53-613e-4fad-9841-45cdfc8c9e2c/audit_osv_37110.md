# [M] Vim has Heap-based Buffer Overflow in Emacs tags parsing

## Summary
Severity: Medium
Advisory: CVE-2026-28418
Aliases: GHSA-h4mf-vg97-hj8j
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-28418
Type: osv

## Details
Vim is an open source, command line text editor. Prior to version 9.2.0074, a heap-based buffer overflow out-of-bounds read exists in Vim's Emacs-style tags file parsing logic. When processing a malformed tags file, Vim can be tricked into reading up to 7 bytes beyond the allocated memory boundary. Version 9.2.0074 fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/02/27/7
- https://github.com/vim/vim/releases/tag/v9.2.0074
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28418.json
- https://github.com/vim/vim/security/advisories/GHSA-h4mf-vg97-hj8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-28418
- https://github.com/vim/vim/commit/f6a7f469a9c0d09e84cd6cb
