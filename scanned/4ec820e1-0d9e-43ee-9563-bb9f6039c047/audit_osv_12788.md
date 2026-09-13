# [M] CVE-2018-14876

## Summary
Severity: Medium
Advisory: CVE-2018-14876
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-03
Source: https://osv.dev/vulnerability/CVE-2018-14876
Type: osv

## Details
An issue was discovered in image_save_png in image/image-png.cpp in Free Lossless Image Format (FLIF) 0.3. Attackers can trigger a longjmp that leads to an uninitialized stack frame after a libpng error concerning the IHDR image width.

## References
- https://github.com/FLIF-hub/FLIF/issues/520
