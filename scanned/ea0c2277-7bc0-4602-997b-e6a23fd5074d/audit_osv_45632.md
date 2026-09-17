# [C] JLSEC-2026-146

## Summary
Severity: Critical
Advisory: JLSEC-2026-146
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-146
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.8+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From version 3.4.0 to before version 3.4.8, a crafted B44 or B44A EXR file can cause an out-of-bounds write in any application that decodes it via `exr_decoding_run()`. Consequences range from immediate crash (most likely) to corruption of adjacent heap allocations (layout-dependent). This issue has been patched in version 3.4.8.

## References
- https://github.com/AcademySoftwareFoundation/openexr/commit/35e7aa35e22c1975606be86e859f31cc1fc598ee
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.8
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-h762-rhv3-h25v
