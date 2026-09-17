# [M] OpenEXR: Scratch buffer overflow decoding B44-compressed InputFile on ILP32

## Summary
Severity: Medium
Advisory: CVE-2026-59984
Aliases: GHSA-92pq-9qv4-g68q
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59984
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions 3.1.0 through 3.2.10, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 are vulnerable on ILP32 builds to an out-of-bounds write. When a crafted B44-compressed scanline EXR causes the logical scratch size to truncate before allocation and uncompress_b44_impl() writes using the attacker-controlled channel width, allowing denial of service and memory corruption. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.11
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.13
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.14
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-92pq-9qv4-g68q
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59984.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59984
