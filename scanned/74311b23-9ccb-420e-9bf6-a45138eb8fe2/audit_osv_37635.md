# [M] ImageMagick has a possible stack buffer overflow in sixel encoder

## Summary
Severity: Medium
Advisory: CVE-2026-32259
Aliases: GHSA-49hx-7656-jpg3
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-03-12
Source: https://osv.dev/vulnerability/CVE-2026-32259
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to 7.1.2-16 and 6.9.13-41, when a memory allocation fails in the sixel encoder it would be possible to write past the end of a buffer on the stack. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32259.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-49hx-7656-jpg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32259
