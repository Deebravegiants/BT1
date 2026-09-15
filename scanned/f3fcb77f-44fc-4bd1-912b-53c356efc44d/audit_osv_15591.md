# [C] CVE-2019-17539

## Summary
Severity: Critical
Advisory: CVE-2019-17539
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-14
Source: https://osv.dev/vulnerability/CVE-2019-17539
Type: osv

## Details
In FFmpeg before 4.2, avcodec_open2 in libavcodec/utils.c allows a NULL pointer dereference and possibly unspecified other impact when there is no valid close function pointer.

## References
- https://lists.debian.org/debian-lts-announce/2021/01/msg00026.html
- https://security.gentoo.org/glsa/202003-65
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2020/dsa-4722
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15733
- https://github.com/FFmpeg/FFmpeg/commit/8df6884832ec413cf032dfaa45c23b1c7876670c
