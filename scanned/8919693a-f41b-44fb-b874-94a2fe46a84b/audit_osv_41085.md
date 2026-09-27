# [M] Vim: Out-of-bounds Read in Text Property Count

## Summary
Severity: Medium
Advisory: CVE-2026-57451
Aliases: GHSA-f36c-2qcp-7gpw
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57451
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0670, get_text_props() in src/textprop.c reads a uint16 property count stored inline after a line's text and returns it as the number of 32-byte textprop_T entries that follow. The only check is a floor that guarantees room for a single entry; the count is never checked against the amount of data actually present. A line that declares a large count while carrying little data causes consumers to read far past the end of the line buffer. Such a line can be delivered through a crafted undo file, leading to a crash. This vulnerability is fixed in 9.2.0670.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0670
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57451.json
- https://github.com/vim/vim/security/advisories/GHSA-f36c-2qcp-7gpw
- https://nvd.nist.gov/vuln/detail/CVE-2026-57451
- https://github.com/vim/vim/commit/b2338ca90643e2f01ecb6547c1172716aaec4f79
