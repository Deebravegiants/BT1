# [C] JLSEC-2026-569

## Summary
Severity: Critical
Advisory: JLSEC-2026-569
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-05
Source: https://osv.dev/vulnerability/JLSEC-2026-569
Type: osv

## Affected
- Julia: `OpenCV_jll` — affected >=4.10.0+0 <4.13.0+0

## Details
OpenCV is an Open Source Computer Vision Library. Versions 4.10.0 and 4.11.0 have an uninitialized pointer variable on stack that may lead to arbitrary heap buffer write when reading crafted JPEG images. Version 4.12.0 fixes the vulnerability.

## References
- https://github.com/opencv/opencv/commit/a39db41390de546d18962ee1278bd6dbb715f466
- https://github.com/opencv/opencv/issues/27271
- https://github.com/opencv/opencv/releases/tag/4.12.0
- https://securitylab.github.com/advisories/GHSL-2025-057_OpenCV/
