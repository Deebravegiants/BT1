# [M] JLSEC-2026-158

## Summary
Severity: Medium
Advisory: JLSEC-2026-158
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/JLSEC-2026-158
Type: osv

## Affected
- Julia: `libde265_jll` — affected >=0 <1.0.18000+0

## Details
libde265 is an open source implementation of the h.265 video codec. Prior to version 1.0.17, a malformed H.265 PPS NAL unit causes a segmentation fault in `pic_parameter_set::set_derived_values()`. This issue has been patched in version 1.0.17.

## References
- https://github.com/strukturag/libde265/releases/tag/v1.0.17
- https://github.com/strukturag/libde265/security/advisories/GHSA-wqrf-6rf5-v78r
