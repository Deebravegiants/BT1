# [M] Vim: Out-of-bounds Read with libsodium-encrypted Files

## Summary
Severity: Medium
Advisory: CVE-2026-57452
Aliases: GHSA-c4j9-wr9j-4486
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57452
Type: osv

## Details
Vim is an open source, command line text editor. Prior to 9.2.0671, when Vim opens a file encrypted with the VimCrypt~04! or VimCrypt~05!
method (xchacha20poly1305, requires the +sodium feature) whose body is shorter than a single libsodium secretstream header, an unsigned length calculation underflows and a subsequent decryption call reads far past the end of the input buffer, crashing Vim. This vulnerability is fixed in 9.2.0671.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0671
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57452.json
- https://github.com/vim/vim/security/advisories/GHSA-c4j9-wr9j-4486
- https://nvd.nist.gov/vuln/detail/CVE-2026-57452
- https://github.com/vim/vim/commit/c8777cec25dcfae89c42e9aff51af61f71c5745f
