# [H] OpenEXR: Out-of-bounds read in DeepImageChannel::row() for non-zero dataWindow origin

## Summary
Severity: High
Advisory: CVE-2026-59189
Aliases: GHSA-hwmv-39v6-739m
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59189
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. In OpenEXRUtil versions 3.3.0 through 3.3.12 and 3.4.0 through 3.4.12, the documented TypedDeepImageChannel<T>::row() API can return an out-of-bounds pointer when a deep image has a non-zero dataWindow origin, resulting in a heap out-of-bounds read and crash, with potential information disclosure under a controlled heap layout. The flaw arises because ImfDeepImageChannel uses two conflicting coordinate models: at(x, y) uses absolute coordinates (with _base offset by dataWindow.min), while row(r) is documented as 0-based logical access. For a non-zero dataWindow.min, row(0) therefore points outside the _sampleListPointers allocation instead of at the first logical row. This issue is fixed in versions 3.3.13 and 3.4.13.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-hwmv-39v6-739m
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59189.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59189
- https://github.com/AcademySoftwareFoundation/openexr/commit/37f03b6ed90f3dd9910f31de3a40f25f2bc2aca1
- https://github.com/AcademySoftwareFoundation/openexr/commit/55b7958ecb5ac32c427ff39c1e063f6f7bbee77c
- https://github.com/AcademySoftwareFoundation/openexr/commit/aef02224ba282a802de65d16c49c1cdb82089dec
