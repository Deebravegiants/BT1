# [M] CVE-2017-17081

## Summary
Severity: Medium
Advisory: CVE-2017-17081
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-30
Source: https://osv.dev/vulnerability/CVE-2017-17081
Type: osv

## Details
The gmc_mmx function in libavcodec/x86/mpegvideodsp.c in FFmpeg 2.3 and 3.4 does not properly validate widths and heights, which allows remote attackers to cause a denial of service (integer signedness error and out-of-array read) via a crafted MPEG file.

## References
- https://www.debian.org/security/2018/dsa-4099
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=3516#c1
- https://github.com/FFmpeg/FFmpeg/commit/27f8d386829689c346ff0cef00d3af57b9fb8903
- https://github.com/FFmpeg/FFmpeg/commit/58cf31cee7a456057f337b3102a03206d833d5e8
- https://lists.ffmpeg.org/pipermail/ffmpeg-devel/2017-November/219748.html
