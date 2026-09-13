# [H] libheif: Heap Buffer OOB Read in overlay compositing due to wrong alpha stride

## Summary
Severity: High
Advisory: CVE-2026-32882
Aliases: GHSA-hg7q-rjr2-8x46
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-32882
Type: osv

## Details
libheif is a HEIF and AVIF file format decoder and encoder. Versions 1.21.2 and prior contain a heap buffer over-read in HeifPixelImage::overlay() in libheif/pixelimage.cc. When compositing an overlay image (iovl) whose child image has a different bit depth for the alpha channel than for the color channels, the function indexes into the alpha plane using the color channel stride (in_stride) instead of the previously retrieved alpha_stride, causing reads past the end of the alpha buffer (up to 3,123 bytes for a 100×50 image with 10-bit color and 8-bit alpha). A crafted HEIF file can exploit this to cause a denial of service (crash) or potentially disclose adjacent heap memory through leaked bytes embedded in the decoded output pixels. This issue has been fixed in versionThis issue has been fixed in version 1.22.0.

## References
- https://github.com/strukturag/libheif/releases/tag/v1.22.0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-32882.json
- https://access.redhat.com/security/cve/CVE-2026-32882
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32882.json
- https://github.com/strukturag/libheif/security/advisories/GHSA-hg7q-rjr2-8x46
- https://nvd.nist.gov/vuln/detail/CVE-2026-32882
- https://bugzilla.redhat.com/show_bug.cgi?id=2480000
