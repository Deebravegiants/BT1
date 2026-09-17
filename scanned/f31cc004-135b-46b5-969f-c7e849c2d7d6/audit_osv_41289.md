# [H] OpenEXR: exrmetrics deep pixelmode heap buffer overflow

## Summary
Severity: High
Advisory: CVE-2026-59187
Aliases: GHSA-6jj8-cxcr-j8hm
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59187
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions 3.3.0 through 3.3.12 and 3.4.0 through 3.4.13 are vulnerable to a heap out-of-bounds write when exrmetrics reads a crafted deep scanline EXR. This occurs with pixel conversion options such as --pixelmode float or --bench because DeepSlice requests FLOAT output while the backing sample buffers are allocated using the input HALF element size. The issue is fixed in versions 3.3.13 and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-6jj8-cxcr-j8hm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59187.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59187
- https://github.com/AcademySoftwareFoundation/openexr/commit/46e70220dc91dbc1341fac4671704e970b450585
- https://github.com/AcademySoftwareFoundation/openexr/commit/7e772dd704b9b5d6dc2564647d89f7813f608e94
