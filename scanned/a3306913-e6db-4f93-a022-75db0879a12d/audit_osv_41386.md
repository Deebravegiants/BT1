# [M] OpenEXR: Out-of-bounds read in DeepTiledInputFile sample-count table decode on ILP32

## Summary
Severity: Medium
Advisory: CVE-2026-59983
Aliases: GHSA-p42q-g5c9-mh9w
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-59983
Type: osv

## Details
OpenEXR is the reference implementation and specification for the EXR image format, widely used in the motion picture industry. OpenEXR versions before 3.2.11, 3.3.0 through 3.3.12, and 3.4.0 through 3.4.13 are vulnerable on ILP32 builds to an out-of-bounds read. The vulnerability is reached when a crafted uncompressed deep-tile EXR causes the sample-count table size calculation in OpenEXRCore decoding.c to wrap before unpack_sample_table() iterates over the full attacker-controlled tile dimensions, allowing denial of service. This issue is fixed in versions 3.2.11, 3.3.13, and 3.4.14.

## References
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-p42q-g5c9-mh9w
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59983.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59983
- https://github.com/AcademySoftwareFoundation/openexr/commit/0efec58d2d28a0ee322f5028dee6fb57d459580e
- https://github.com/AcademySoftwareFoundation/openexr/commit/78e91146fceeee317820a146ba99a96f380945b8
- https://github.com/AcademySoftwareFoundation/openexr/commit/f0e404f7298cd8563a1d30a64a1c982dbd68fc49
