# [H] OpenEXR: Heap buffer overflow in PyOpenEXR from literal/prefixed RGB channel name collision

## Summary
Severity: High
Advisory: CVE-2026-68513
Aliases: GHSA-rw5h-3q4v-c3vc
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-68513
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. Versions 3.3.0 through 3.3.12 and 3.4.0 through 3.4.13 contain a heap buffer overflow in PyOpenEXR triggered by a channel-name key collision between literal and prefixed RGB channels. When separate_channels=false, PyOpenEXR maps each physical channel name through channelNameToRGBA() and coalesces the results into a shared RGB array. A crafted flat scanline EXR that contains both a literal channel such as left and prefixed channels such as left.R, left.G, and left.B causes these names to collide, so the wrapper reuses an undersized two-dimensional NumPy array for the coalesced RGB slices and writes out of bounds when OpenEXR.File(path) decodes the pixels. This issue is fixed in versions 3.3.13 and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-rw5h-3q4v-c3vc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68513.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68513
- https://github.com/AcademySoftwareFoundation/openexr/commit/c1f3ec0d91cfa5a8035ecd00920835ac76e01640
- https://github.com/AcademySoftwareFoundation/openexr/commit/d134e3cd81a2e343f2919e86bf949f576b1ab16a
