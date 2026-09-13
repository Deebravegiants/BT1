# [H] CVE-2019-19777

## Summary
Severity: High
Advisory: CVE-2019-19777
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-13
Source: https://osv.dev/vulnerability/CVE-2019-19777
Type: osv

## Details
stb_image.h (aka the stb image loader) 2.23, as used in libsixel and other products, has a heap-based buffer over-read in stbi__load_main.

## References
- https://github.com/saitoha/libsixel/issues/109
