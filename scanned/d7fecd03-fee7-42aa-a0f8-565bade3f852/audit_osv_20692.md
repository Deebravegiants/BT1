# [H] CVE-2021-3610

## Summary
Severity: High
Advisory: CVE-2021-3610
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-02-24
Source: https://osv.dev/vulnerability/CVE-2021-3610
Type: osv

## Details
A heap-based buffer overflow vulnerability was found in ImageMagick in versions prior to 7.0.11-14 in ReadTIFFImage() in coders/tiff.c. This issue is due to an incorrect setting of the pixel array size, which can lead to a crash and segmentation fault.

## References
- https://github.com/fuzzing2026/CVE-PoCs/tree/main/imagemagick-CVE-2021-3610
- http://www.openwall.com/lists/oss-security/2023/05/29/4
- http://www.openwall.com/lists/oss-security/2023/06/05/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1973689
- https://github.com/ImageMagick/ImageMagick/commit/930ff0d1a9bc42925a7856e9ea53f5fc9f318bf3
