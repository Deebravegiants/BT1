# [M] JLSEC-2026-377

## Summary
Severity: Medium
Advisory: JLSEC-2026-377
Ecosystem: Julia
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:L/SI:L/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/JLSEC-2026-377
Type: osv

## Affected
- Julia: `LibVPX_jll` — affected >=0 <1.15.2+0

## Details
There exists interger overflows in libvpx in versions prior to 1.14.1. Calling `vpx_img_alloc()` with a large value of the `d_w`, `d_h`, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned `vpx_image_t` struct may be invalid. Calling `vpx_img_wrap()` with a large value of the `d_w`, `d_h`, or `stride_align` parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned `vpx_image_t` struct may be invalid. We recommend upgrading to version 1.14.1 or beyond

## References
- https://g-issues.chromium.org/issues/332382766
- https://lists.debian.org/debian-lts-announce/2024/06/msg00005.html
