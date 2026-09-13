# [H] CVE-2018-13037

## Summary
Severity: High
Advisory: CVE-2018-13037
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-01
Source: https://osv.dev/vulnerability/CVE-2018-13037
Type: osv

## Details
An issue was discovered in jpeg-compressor 0.1. The bmp_load function in stb_image.c allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact.

## References
- https://github.com/kornelski/jpeg-compressor/issues/13
- https://github.com/fouzhe/security/tree/master/jpeg-compressor
