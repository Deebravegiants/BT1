# [M] ImageMagick: Heap BufferOverflow write of single zero byte when parsing XML

## Summary
Severity: Medium
Advisory: CVE-2026-33899
Aliases: GHSA-cr67-pvmx-2pp2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-33899
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below 7.1.2-189 and 6.9.13-44, when `Magick` parses an XML file it is possible that a single zero byte is written out of the bounds. This issue has been fixed in versions 6.9.13-44 and 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33899.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-cr67-pvmx-2pp2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33899
- https://github.com/ImageMagick/ImageMagick/commit/ae679e2fd19ec656bfab9f822ae4cf06bf91604d
