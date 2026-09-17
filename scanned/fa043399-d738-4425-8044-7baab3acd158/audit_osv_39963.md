# [M] ImageMagick: Heap Buffer Underwrite in Floyd-Steinberg depth dithering

## Summary
Severity: Medium
Advisory: CVE-2026-48724
Aliases: GHSA-2hhq-c99x-492r
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-48724
Type: osv

## Details
ImageMagick is free and open-source software used for editing and manipulating digital images. Prior to version 7.1.2-24, when using an image with mask the Floyd-Steinberg dithering method it will cause a negative heap buffer over-write. This issue has been patched in version 7.1.2-24.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48724.json
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-2hhq-c99x-492r
- https://nvd.nist.gov/vuln/detail/CVE-2026-48724
