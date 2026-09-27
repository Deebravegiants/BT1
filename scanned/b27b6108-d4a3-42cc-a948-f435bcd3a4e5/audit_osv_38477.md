# [C] OpenEXR has integer overflow in DWA setupChannelData planarUncRle pointer arithmetic (missed variant of CVE-2026-34589)

## Summary
Severity: Critical
Advisory: CVE-2026-40244
Aliases: GHSA-j526-66f6-fxhx
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40244
Type: osv

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In versions 3.4.0 through 3.4.9, 3.3.0 through 3.3.9, and 3.2.0 through 3.2.7, `internal_dwa_compressor.h:1722` performs `curc->width * curc->height` in `int32` arithmetic without a `(size_t)` cast. This is the same overflow pattern fixed in other locations by the recent CVE-2026-34589 batch, but this line was missed. Versions 3.4.10, 3.3.10, and 3.2.8 contain a fix that addresses `internal_dwa_compressor.h:1722`.

## References
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.8
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.10
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.10
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40244.json
- https://access.redhat.com/security/cve/CVE-2026-40244
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-j526-66f6-fxhx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40244.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40244
- https://bugzilla.redhat.com/show_bug.cgi?id=2459955
