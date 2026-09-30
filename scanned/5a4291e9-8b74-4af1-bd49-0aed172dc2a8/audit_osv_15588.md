# [H] CVE-2019-17534

## Summary
Severity: High
Advisory: CVE-2019-17534
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-10-13
Source: https://osv.dev/vulnerability/CVE-2019-17534
Type: osv

## Details
vips_foreign_load_gif_scan_image in foreign/gifload.c in libvips before 8.8.2 tries to access a color map before a DGifGetImageDesc call, leading to a use-after-free.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=16796
- https://github.com/libvips/libvips/commit/ce684dd008532ea0bf9d4a1d89bacb35f4a83f4d
- https://github.com/libvips/libvips/compare/v8.8.1...v8.8.2
