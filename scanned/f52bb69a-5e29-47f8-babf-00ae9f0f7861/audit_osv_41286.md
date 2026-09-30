# [M] OpenEXR: Signed Integer Overflow Leading to Out-of-Bounds Memory Access in Deep Tile Decoding

## Summary
Severity: Medium
Advisory: CVE-2026-59183
Aliases: GHSA-rqp5-pmwm-wj6x
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59183
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In versions 3.1.0 through 3.2.10, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13, an int32_t multiplication in OpenEXRCore's unpack_sample_table() can overflow while decoding a crafted deep tiled EXR file, producing an invalid pointer that leads to a read from an unmapped memory address and a crash. Because the overflow occurs in the standard decoding path (exr_decoding_run), any application that decodes deep tiled EXR files is affected. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-rqp5-pmwm-wj6x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59183.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59183
- https://github.com/AcademySoftwareFoundation/openexr/commit/5e55a64ad1f119a8166542f4b6e034c31b7e043a
- https://github.com/AcademySoftwareFoundation/openexr/commit/a6cf183725b5665ac3fdbec640125fba5ee1ab39
- https://github.com/AcademySoftwareFoundation/openexr/commit/e2adb5be3bbc3a1f82f2bc06cc9699995a99a607
