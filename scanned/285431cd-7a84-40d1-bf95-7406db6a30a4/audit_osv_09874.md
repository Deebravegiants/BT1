# [M] CVE-2017-11755

## Summary
Severity: Medium
Advisory: CVE-2017-11755
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-30
Source: https://osv.dev/vulnerability/CVE-2017-11755
Type: osv

## Details
The WritePICONImage function in coders/xpm.c in ImageMagick 7.0.6-4 allows remote attackers to cause a denial of service (memory leak) via a crafted file that is mishandled in an AcquireSemaphoreInfo call.

## References
- https://github.com/ImageMagick/ImageMagick/issues/634
