# [M] ImageMagick has a Heap Overflow when writing extremely large image profile in the PNG encoder

## Summary
Severity: Medium
Advisory: CVE-2026-30883
Aliases: GHSA-qmw5-2p58-xvrc
CVSS: 5.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-09
Source: https://osv.dev/vulnerability/CVE-2026-30883
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 7.1.2-16 and 6.9.13-41, an extremely large image profile could result in a heap overflow when encoding a PNG image. This vulnerability is fixed in 7.1.2-16 and 6.9.13-41.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30883.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-qmw5-2p58-xvrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-30883
