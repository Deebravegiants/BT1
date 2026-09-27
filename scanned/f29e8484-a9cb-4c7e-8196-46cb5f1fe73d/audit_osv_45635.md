# [C] JLSEC-2026-149

## Summary
Severity: Critical
Advisory: JLSEC-2026-149
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-149
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.9+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From 3.2.0 to before 3.2.7, 3.3.9, and 3.4.9, the DWA lossy decoder constructs temporary per-component block pointers using signed 32-bit arithmetic. For a large enough width, the calculation overflows and later decoder stores operate on a wrapped pointer outside the allocated rowBlock backing store. This vulnerability is fixed in 3.2.7, 3.3.9, and 3.4.9.

## References
- https://access.redhat.com/security/cve/CVE-2026-34589
- https://bugzilla.redhat.com/show_bug.cgi?id=2455411
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.7
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.9
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.9
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-p8xc-w3q4-h64x
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34589.json
