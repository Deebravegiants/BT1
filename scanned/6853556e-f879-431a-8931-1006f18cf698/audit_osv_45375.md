# [M] JLSEC-2026-1097

## Summary
Severity: Medium
Advisory: JLSEC-2026-1097
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1097
Type: osv

## Affected
- Julia: `libheif_jll` — affected >=0 <1.22.2000+0

## Details
libheif is a HEIF and AVIF file format decoder and encoder. The fix for CVE-2026-3949 (commit `b97c8b5`, PR #1712) introduced an integer overflow in the very security check it added. The check itself can be bypassed, allowing a crafted HEIF file with a VVC track to trigger the same out-of-bounds heap read that CVE-2026-3949 was meant to prevent. This is a separate, currently-unpatched vulnerability. Issue #1712 was closed as fixed without testing the edge case where `size` is near `UINT32_MAX`. Version 1.22.0 patches the issue.

## References
- https://github.com/strukturag/libheif/issues/1712
- https://github.com/strukturag/libheif/security/advisories/GHSA-p6q9-fhf2-vj9v
