# [C] Integer overflow in OpenEXR's `internal_dwa_compressor`

## Summary
Severity: Critical
Advisory: JLSEC-2026-807
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/JLSEC-2026-807
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.12+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. In versions 3.4.0 through 3.4.9, 3.3.0 through 3.3.9, and 3.2.0 through 3.2.7, `internal_dwa_compressor.h:1722` performs `curc->width * curc->height` in `int32` arithmetic without a `(size_t)` cast. This is the same overflow pattern fixed in other locations by the recent CVE-2026-34589 batch, but this line was missed. Versions 3.4.10, 3.3.10, and 3.2.8 contain a fix that addresses `internal_dwa_compressor.h:1722`.

## References
- https://access.redhat.com/security/cve/CVE-2026-40244
- https://bugzilla.redhat.com/show_bug.cgi?id=2459955
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.8
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.10
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.10
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-j526-66f6-fxhx
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40244.json
