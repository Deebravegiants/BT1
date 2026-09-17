# [M] OpenEXR: Heap out-of-bounds read in OpenEXRCore RLE decoding on ILP32

## Summary
Severity: Medium
Advisory: CVE-2026-59985
Aliases: GHSA-v6v5-344m-64vm
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59985
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions 3.2.0 through 3.2.10, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 are vulnerable on ILP32 builds to a heap out-of-bounds read. The issue occurs when a crafted RLE-compressed EXR causes the 64-bit unpacked size to truncate before allocation in OpenEXRCore decoding.c and unpack_32bit() reads beyond the resulting buffer, allowing denial of service. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.11
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.13
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.14
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-v6v5-344m-64vm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59985.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59985
