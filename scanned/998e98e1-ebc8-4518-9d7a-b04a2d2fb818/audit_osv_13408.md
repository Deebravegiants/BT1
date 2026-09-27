# [M] CVE-2018-19759

## Summary
Severity: Medium
Advisory: CVE-2018-19759
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19759
Type: osv

## Details
There is a heap-based buffer over-read at stb_image_write.h (function: stbi_write_png_to_mem) in libsixel 1.8.2 that will cause a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1649202
