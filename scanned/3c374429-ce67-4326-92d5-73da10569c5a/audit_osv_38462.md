# [M] ImageMagick: Heap buffer overflow when encoding JXL image with a 16-bit float

## Summary
Severity: Medium
Advisory: CVE-2026-40183
Aliases: GHSA-jvgr-9ph5-m8v4
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/CVE-2026-40183
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. In versions below 7.1.2-19, the JXL encoder has an heap write overflow when a user specifies that the image should be encoded as 16 bit floats. This issue has been fixed in version 7.1.2-19.

## References
- https://github.com/ImageMagick/ImageMagick/releases/tag/7.1.2-19
- https://github.com/dlemstra/Magick.NET/releases/tag/14.12.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40183.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-jvgr-9ph5-m8v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40183
