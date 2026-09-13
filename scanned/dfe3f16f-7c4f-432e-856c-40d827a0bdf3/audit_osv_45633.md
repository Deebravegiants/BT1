# [C] JLSEC-2026-147

## Summary
Severity: Critical
Advisory: JLSEC-2026-147
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-147
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.4.4+0 <3.4.8+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From version 3.4.0 to before version 3.4.7, an attacker providing a crafted .exr file with HTJ2K compression and a channel width of 32768 can write controlled data beyond the output heap buffer in any application that decodes EXR images. The write primitive is 2 bytes per overflow iteration or 4 bytes (by another path), repeating for each additional pixel past the overflow point. In this context, a heap write overflow can lead to remote code execution on systems. This issue has been patched in version 3.4.7.

## References
- https://access.redhat.com/security/cve/CVE-2026-34545
- https://bugzilla.redhat.com/show_bug.cgi?id=2454139
- https://github.com/AcademySoftwareFoundation/openexr/commit/3827998f5c041d6a94c6af24bbb363daa669e4b3
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.7
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-ghfj-fx47-wg97
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-34545.json
