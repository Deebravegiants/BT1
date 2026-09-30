# [M] OpenEXR: Empty multiView viewFromChannelName file crash

## Summary
Severity: Medium
Advisory: CVE-2026-61555
Aliases: GHSA-g8f2-r72m-48vx
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-61555
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions before 3.2.11, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 are vulnerable to crashing. This occurs when Imf::GetChannelsInMultiPartFile() processes a crafted EXR with an empty multiView header attribute and Imf::viewFromChannelName() indexes the empty vector for a dotless channel name. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-g8f2-r72m-48vx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61555
- https://github.com/AcademySoftwareFoundation/openexr/commit/6c6bc2d485f1435d3776b3b4a36f1617cf87070b
- https://github.com/AcademySoftwareFoundation/openexr/commit/b4257c7740a05071262e496ae7e7efa4774712f5
- https://github.com/AcademySoftwareFoundation/openexr/commit/c6d3796918f8e358c9c329e909fa6b0dd7dc8cb9
