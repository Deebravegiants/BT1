# [M] Vim: Out-of-bounds Read with Text Properties

## Summary
Severity: Medium
Advisory: CVE-2026-57454
Aliases: GHSA-ww8h-47xp-hp4w
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57454
Type: osv

## Details
Vim is an open source, command line text editor. From 9.2.0320 until 9.2.0679, a crafted undo or swap file can store a virtual-text property whose offset and length point outside the line's property data. When Vim restores or displays such a line it converts the offset into a pointer and reads the virtual text without bounds checking, causing an out-of-bounds read that can crash Vim or disclose adjacent heap memory. This vulnerability is fixed in 9.2.0679.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0679
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57454.json
- https://github.com/vim/vim/security/advisories/GHSA-ww8h-47xp-hp4w
- https://nvd.nist.gov/vuln/detail/CVE-2026-57454
- https://github.com/vim/vim/commit/b3faeecc976d3031d7c0675623516ec60c30f949
