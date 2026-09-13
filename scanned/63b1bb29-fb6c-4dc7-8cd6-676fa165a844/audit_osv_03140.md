# [C] ALPINE-CVE-2024-5171

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-5171
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-5171
Type: osv

## Affected
- Alpine:v3.20: `aom` — affected >=0 <3.9.1-r0
- Alpine:v3.21: `aom` — affected >=0 <3.9.1-r0
- Alpine:v3.22: `aom` — affected >=0 <3.9.1-r0
- Alpine:v3.23: `aom` — affected >=0 <3.9.1-r0
- Alpine:v3.24: `aom` — affected >=0 <3.9.1-r0

## Details
Integer overflow in libaom internal function img_alloc_helper can lead to heap buffer overflow. This function can be reached via 3 callers:


  *  Calling aom_img_alloc() with a large value of the d_w, d_h, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.
  *  Calling aom_img_wrap() with a large value of the d_w, d_h, or align parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.
  *  Calling aom_img_alloc_with_border() with a large value of the d_w, d_h, align, size_align, or border parameter may result in integer overflows in the calculations of buffer sizes and offsets and some fields of the returned aom_image_t struct may be invalid.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-5171
