# [H] CVE-2021-37789

## Summary
Severity: High
Advisory: CVE-2021-37789
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2022-11-02
Source: https://osv.dev/vulnerability/CVE-2021-37789
Type: osv

## Details
stb_image.h 2.27 has a heap-based buffer over in stbi__jpeg_load, leading to Information Disclosure or Denial of Service.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00045.html
- https://github.com/nothings/stb/issues/1178
