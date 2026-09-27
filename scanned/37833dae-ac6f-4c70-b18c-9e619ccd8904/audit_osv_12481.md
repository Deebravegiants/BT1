# [M] CVE-2018-12460

## Summary
Severity: Medium
Advisory: CVE-2018-12460
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12460
Type: osv

## Details
libavcodec in FFmpeg 4.0 may trigger a NULL pointer dereference if the studio profile is incorrectly detected while converting a crafted AVI file to MPEG4, leading to a denial of service, related to idctdsp.c and mpegvideo.c.

## References
- https://github.com/FFmpeg/FFmpeg/commit/b3332a182f8ba33a34542e4a0370f38b914ccf7d
