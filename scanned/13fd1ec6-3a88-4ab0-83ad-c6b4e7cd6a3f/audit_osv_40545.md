# [M] ImageMagick: Memory Leak in wand option parser when providing invalid arguments

## Summary
Severity: Medium
Advisory: CVE-2026-53464
Aliases: GHSA-j989-f892-2335
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-53464
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-25, when providing invalid options to the wand option parser a small memory leak will occur. This issue has been patched in version 7.1.2-25.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53464.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-j989-f892-2335
- https://nvd.nist.gov/vuln/detail/CVE-2026-53464
