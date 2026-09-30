# [H] CVE-2015-8661

## Summary
Severity: High
Advisory: CVE-2015-8661
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2015-12-24
Source: https://osv.dev/vulnerability/CVE-2015-8661
Type: osv

## Details
The h264_slice_header_init function in libavcodec/h264_slice.c in FFmpeg before 2.8.3 does not validate the relationship between the number of threads and the number of slices, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via crafted H.264 data.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=4ea4d2f438c9a7eba37980c9a87be4b34943e4d5
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00004.html
- http://www.securitytracker.com/id/1034539
- https://lists.debian.org/debian-lts-announce/2018/12/msg00009.html
