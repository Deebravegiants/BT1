# [H] CVE-2016-3062

## Summary
Severity: High
Advisory: CVE-2016-3062
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-16
Source: https://osv.dev/vulnerability/CVE-2016-3062
Type: osv

## Details
The mov_read_dref function in libavformat/mov.c in Libav before 11.7 and FFmpeg before 0.11 allows remote attackers to cause a denial of service (memory corruption) or execute arbitrary code via the entries value in a dref box in an MP4 file.

## References
- https://ffmpeg.org/security.html
- https://git.libav.org/?p=libav.git%3Ba=commit%3Bh=7e01d48cfd168c3dfc663f03a3b6a98e0ecba328
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00105.html
- http://www.debian.org/security/2016/dsa-3603
- https://libav.org/releases/libav-11.7.changelog
- https://security.gentoo.org/glsa/201705-08
- https://bugzilla.libav.org/show_bug.cgi?id=929
- https://github.com/FFmpeg/FFmpeg/commit/689e59b7ffed34eba6159dcc78e87133862e3746
