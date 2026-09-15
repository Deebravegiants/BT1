# [C] OpenEXR: integer overflow lead to OOB in HTJ2K decoder

## Summary
Severity: Critical
Advisory: CVE-2026-34545
Aliases: GHSA-ghfj-fx47-wg97
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34545
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From version 3.4.0 to before version 3.4.7, an attacker providing a crafted .exr file with HTJ2K compression and a channel width of 32768 can write controlled data beyond the output heap buffer in any application that decodes EXR images. The write primitive is 2 bytes per overflow iteration or 4 bytes (by another path), repeating for each additional pixel past the overflow point. In this context, a heap write overflow can lead to remote code execution on systems. This issue has been patched in version 3.4.7.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.7
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34545.json
- https://access.redhat.com/security/cve/CVE-2026-34545
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-ghfj-fx47-wg97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34545.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-34545
- https://bugzilla.redhat.com/show_bug.cgi?id=2454139
- https://github.com/AcademySoftwareFoundation/openexr/commit/3827998f5c041d6a94c6af24bbb363daa669e4b3
