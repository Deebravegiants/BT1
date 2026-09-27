# [H] OpenEXR: DWAA InputFile AC buffer overflow on ILP32 platforms

## Summary
Severity: High
Advisory: CVE-2026-59982
Aliases: GHSA-6662-fq6f-93mp
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59982
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions before 3.2.11, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 can return an out-of-bounds pointer from TypedDeepImageChannel::row() when a crafted deep EXR has a nonzero dataWindow origin. This vulnerability occurs because the API combines zero-based row access with an absolute-coordinate-adjusted base pointer, allowing a crash or limited information disclosure. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-6662-fq6f-93mp
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59982.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59982
- https://github.com/AcademySoftwareFoundation/openexr/commit/37f03b6ed90f3dd9910f31de3a40f25f2bc2aca1
- https://github.com/AcademySoftwareFoundation/openexr/commit/55b7958ecb5ac32c427ff39c1e063f6f7bbee77c
- https://github.com/AcademySoftwareFoundation/openexr/commit/aef02224ba282a802de65d16c49c1cdb82089dec
