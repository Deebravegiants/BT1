# [C] JLSEC-2026-122

## Summary
Severity: Critical
Advisory: JLSEC-2026-122
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/JLSEC-2026-122
Type: osv

## Affected
- Julia: `libaom_jll` — affected >=0 <3.11.0+0

## Details
Integer overflow in libaom internal function `img_alloc_helper` can lead to heap buffer overflow. This function can be reached via 3 callers:

  - Calling `aom_img_alloc()` with a large value of the `d_w`, `d_h`, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned `aom_image_t` struct may be invalid.
  - Calling `aom_img_wrap()` with a large value of the `d_w`, `d_h`, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned `aom_image_t` struct may be invalid.
  - Calling `aom_img_alloc_with_border()` with a large value of the `d_w`, `d_h`, align, `size_align`, or border parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned `aom_image_t` struct may be invalid.

## References
- https://issues.chromium.org/issues/332382766
- https://lists.debian.org/debian-lts-announce/2024/09/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HYUEHZ35ZPY2EONVZCGO6LPT3AMLZCP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U5NRNCEYS246CYGOR32MF7OGKWOWER22/
