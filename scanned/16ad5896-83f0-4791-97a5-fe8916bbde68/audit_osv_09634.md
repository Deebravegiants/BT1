# [M] CVE-2017-1000460

## Summary
Severity: Medium
Advisory: CVE-2017-1000460
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-03
Source: https://osv.dev/vulnerability/CVE-2017-1000460
Type: osv

## Details
In line libavcodec/h264dec.c:500 in libav(v13_dev0), ffmpeg(n3.4), chromium(56 prior Feb 13, 2017), the return value of init_get_bits is ignored and get_ue_golomb(&gb) is called on an uninitialized get_bits context, which causes a NULL deref exception.

## References
- https://lists.debian.org/debian-lts-announce/2019/03/msg00041.html
- https://bugzilla.libav.org/show_bug.cgi?id=952
- https://chromium.googlesource.com/chromium/third_party/ffmpeg/+/8e313ca08800178efce00045e07dc494d437b70c
- https://lists.ffmpeg.org/pipermail/ffmpeg-cvslog/2017-January/104221.html
