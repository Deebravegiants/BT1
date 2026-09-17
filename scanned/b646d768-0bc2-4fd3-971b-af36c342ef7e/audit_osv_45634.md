# [C] JLSEC-2026-148

## Summary
Severity: Critical
Advisory: JLSEC-2026-148
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-148
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.1+0 <3.4.9+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From 3.1.0 to before 3.2.7, 3.3.9, and 3.4.9, `internal_exr_undo_piz()` advances the working wavelet pointer with signed 32-bit arithmetic. Because nx, ny, and wcount are int, a crafted EXR file can make this product overflow and wrap. The next channel then decodes from an incorrect address. The wavelet decode path operates in place, so this yields both out-of-bounds reads and out-of-bounds writes. This vulnerability is fixed in 3.2.7, 3.3.9, and 3.4.9.

## References
- https://access.redhat.com/errata/RHSA-2026:15887
- https://access.redhat.com/errata/RHSA-2026:15888
- https://access.redhat.com/errata/RHSA-2026:17656
- https://access.redhat.com/errata/RHSA-2026:17658
- https://access.redhat.com/errata/RHSA-2026:17659
- https://access.redhat.com/errata/RHSA-2026:17660
- https://access.redhat.com/errata/RHSA-2026:19146
- https://access.redhat.com/errata/RHSA-2026:19359
- https://access.redhat.com/errata/RHSA-2026:19587
- https://access.redhat.com/errata/RHSA-2026:30078
- https://access.redhat.com/errata/RHSA-2026:30087
- https://access.redhat.com/errata/RHSA-2026:30088
- https://access.redhat.com/errata/RHSA-2026:30089
- https://access.redhat.com/security/cve/CVE-2026-34588
- https://bugzilla.redhat.com/show_bug.cgi?id=2455408
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.2.7
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.3.9
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.9
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-588r-cr5c-w6hf
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34588.json
