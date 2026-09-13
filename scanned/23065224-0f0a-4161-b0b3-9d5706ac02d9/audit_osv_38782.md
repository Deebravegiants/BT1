# [H] OpenEXR: Out-of-bounds read in `IDManifest::init()` during prefix expansion

## Summary
Severity: High
Advisory: CVE-2026-42216
Aliases: GHSA-65j8-95g9-jgj4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-42216
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From versions 3.0.0 to before 3.2.9, 3.3.0 to before 3.3.11, and 3.4.0 to before 3.4.11, IDManifest::init() reconstructs strings from a prefix-compressed representation. If the previous string is longer than 255 bytes, the next string is expected to begin with a 2-byte prefix length. The code reads stringList[i][0] and stringList[i][1] without checking that the current string has at least two bytes. This issue has been patched in versions 3.2.9, 3.3.11, and 3.4.11.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42216.json
- https://access.redhat.com/errata/RHSA-2026:38498
- https://access.redhat.com/errata/RHSA-2026:38499
- https://access.redhat.com/errata/RHSA-2026:39024
- https://access.redhat.com/errata/RHSA-2026:39025
- https://access.redhat.com/errata/RHSA-2026:39026
- https://access.redhat.com/errata/RHSA-2026:39027
- https://access.redhat.com/security/cve/CVE-2026-42216
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-65j8-95g9-jgj4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42216
- https://bugzilla.redhat.com/show_bug.cgi?id=2467633
