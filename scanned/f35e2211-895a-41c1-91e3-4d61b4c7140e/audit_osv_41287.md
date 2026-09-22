# [H] OpenEXR: OpenEXRUtil FlatImageChannel row nonzero dataWindow heap OOB write

## Summary
Severity: High
Advisory: CVE-2026-59184
Aliases: GHSA-pqp9-558c-453q
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59184
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. Versions before 3.2.11, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 allow a crafted EXR with a nonzero dataWindow.min to make TypedFlatImageChannel::row() return an invalid heap pointer, causing out-of-bounds or use-after-free writes. This occurs when an application writes rows through FlatHalfChannel::row(). Affected consumers are tools, converters, render pipeline components, or image-processing services that accept untrusted EXR files and use FlatHalfChannel::row() on loaded images. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-pqp9-558c-453q
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59184.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59184
- https://github.com/AcademySoftwareFoundation/openexr/commit/37f03b6ed90f3dd9910f31de3a40f25f2bc2aca1
- https://github.com/AcademySoftwareFoundation/openexr/commit/55b7958ecb5ac32c427ff39c1e063f6f7bbee77c
- https://github.com/AcademySoftwareFoundation/openexr/commit/aef02224ba282a802de65d16c49c1cdb82089dec
