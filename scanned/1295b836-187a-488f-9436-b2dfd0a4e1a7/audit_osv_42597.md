# [M] OpenEXR: HTJ2K SIZ image-offset gap stack buffer overflow

## Summary
Severity: Medium
Advisory: CVE-2026-68516
Aliases: GHSA-fw66-6xph-56jm
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-68516
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. From version 3.4.0 through 3.4.13, a crafted HTJ2K-compressed EXR can crash OpenEXR during normal decode. An HTJ2K-compressed EXR whose JPEG 2000 SIZ fields place the first tile outside the visible image can reach invalid tile and codeblock geometry in the vendored OpenJPH AVX2 decoder, causing a stack out-of-bounds write and denial of service. OpenEXR's HTJ2K path validates the decoded codestream dimensions against the EXR chunk size, but it does not reject SIZ image-offset/tile-grid geometry where the first tile does not intersect the image. This issue is fixed in version 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-fw66-6xph-56jm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68516.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68516
- https://github.com/AcademySoftwareFoundation/openexr/commit/45521f92104373b5c850f27f2d4659ab6759e848
- https://github.com/AcademySoftwareFoundation/openexr/commit/85009d840cc085aa96ad03ae76fa6463defeb0e5
