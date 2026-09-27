# [M] ImageMagick: Use-After-Free in crafted 8BIM when identifying an image

## Summary
Severity: Medium
Advisory: CVE-2026-55510
Aliases: GHSA-ff5c-8x9r-8qcw
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2026-55510
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to versions 6.9.13-51 and 7.1.2-26, when identifying an image with a crafted 8BIM profile with a specific format string a use-after-free will occur. This issue has been fixed in versions 6.9.13-51 and 7.1.2-26.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55510.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-ff5c-8x9r-8qcw
- https://nvd.nist.gov/vuln/detail/CVE-2026-55510
