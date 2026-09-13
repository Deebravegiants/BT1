# [H] CVE-2019-14373

## Summary
Severity: High
Advisory: CVE-2019-14373
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-28
Source: https://osv.dev/vulnerability/CVE-2019-14373
Type: osv

## Details
An issue was discovered in image_save_png in image/image-png.cpp in Free Lossless Image Format (FLIF) 0.3. Attackers can trigger a heap-based buffer over-read in libpng via a crafted flif file.

## References
- https://github.com/FLIF-hub/FLIF/issues/541
