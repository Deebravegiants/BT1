# [H] OpenEXR: Heap out-of-bounds write in exrmultiview with subsampled channel union

## Summary
Severity: High
Advisory: CVE-2026-68515
Aliases: GHSA-gjf7-wjjw-xq56
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-68515
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In versions before 3.2.11, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13, exrmultiview can write past a heap allocation when it combines two attacker-supplied, individually valid scanline EXR files whose union dataWindow is not aligned to one view's channel subsampling. The utility allocates sampled channel storage using a truncated union_width / xSampling, then reads the sampled input through a Slice based on the misaligned union window, producing a heap out-of-bounds write. The trigger is normal public-tool processing, such as exrmultiview left A.exr right B.exr out.exr with crafted but valid inputs, so this is not solely an API or caller-precondition issue. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-gjf7-wjjw-xq56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68515.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68515
- https://github.com/AcademySoftwareFoundation/openexr/commit/77ee19c021398b1c56f32c3af8347e365dbd4f33
- https://github.com/AcademySoftwareFoundation/openexr/commit/c644ac2dfeac82939c81a8551d6f4b7859f63add
- https://github.com/AcademySoftwareFoundation/openexr/commit/e2300a3d54a93d20a36a86b82f3a506c4c91476f
