# [M] JLSEC-2026-376

## Summary
Severity: Medium
Advisory: JLSEC-2026-376
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:H/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:N/AU:N/R:A/V:D/RE:X/U:X)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-376
Type: osv

## Affected
- Julia: `LibVPX_jll` — affected >=0 <1.15.2+0

## Details
A heap overflow vulnerability exists in libvpx - Encoding a frame that has larger dimensions than the originally configured size with VP9 may result in a heap overflow in libvpx.
We recommend upgrading to version 1.13.1 or above

## References
- https://crbug.com/webm/1642
