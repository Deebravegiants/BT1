# [C] CVE-2024-5171

## Summary
Severity: Critical
Advisory: CVE-2024-5171
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-05
Source: https://osv.dev/vulnerability/CVE-2024-5171
Type: osv

## Details
Integer overflow in libaom internal function img_alloc_helper can lead to heap buffer overflow. This function can be reached via 3 callers:


  *  Calling aom_img_alloc() with a large value of the d_w, d_h, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.
  *  Calling aom_img_wrap() with a large value of the d_w, d_h, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.
  *  Calling aom_img_alloc_with_border() with a large value of the d_w, d_h, align, size_align, or border parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6HYUEHZ35ZPY2EONVZCGO6LPT3AMLZCP/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U5NRNCEYS246CYGOR32MF7OGKWOWER22/
- https://issues.chromium.org/issues/332382766
