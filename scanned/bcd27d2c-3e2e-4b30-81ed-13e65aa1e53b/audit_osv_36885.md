# [M] ImageMagick has heap overflow in pcd decoder that leads to out of bounds read.

## Summary
Severity: Medium
Advisory: CVE-2026-26284
Aliases: GHSA-wrhr-rf8j-r842
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-26284
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-15 and 6.9.13-40, ImageMagick lacks proper boundary checking when processing Huffman-coded data from PCD (Photo CD) files. The decoder contains an function that has an incorrect initialization that could cause an out of bounds read. Versions 7.1.2-15 and 6.9.13-40 contain a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26284.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-wrhr-rf8j-r842
- https://nvd.nist.gov/vuln/detail/CVE-2026-26284
