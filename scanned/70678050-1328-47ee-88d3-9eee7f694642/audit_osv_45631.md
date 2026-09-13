# [M] JLSEC-2026-145

## Summary
Severity: Medium
Advisory: JLSEC-2026-145
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-17
Source: https://osv.dev/vulnerability/JLSEC-2026-145
Type: osv

## Affected
- Julia: `OpenEXR_jll` — affected >=3.1.4+0 <3.4.8+0

## Details
OpenEXR provides the specification and reference implementation of the EXR file format, an image storage format for the motion picture industry. From version 3.4.0 to before version 3.4.8, sensitive information from heap memory may be leaked through the decoded pixel data (information disclosure). This occurs under default settings; simply reading a malicious EXR file is sufficient to trigger the issue, without any user interaction. This issue has been patched in version 3.4.8.

## References
- https://github.com/AcademySoftwareFoundation/openexr/commit/5f6d0aaa9e43802917af7db90f181e88e083d3b8
- https://github.com/AcademySoftwareFoundation/openexr/releases/tag/v3.4.8
- https://github.com/AcademySoftwareFoundation/openexr/security/advisories/GHSA-vc68-257w-m432
