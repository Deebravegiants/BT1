# [H] CVE-2015-8663

## Summary
Severity: High
Advisory: CVE-2015-8663
CVSS: 8.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2015-12-24
Source: https://osv.dev/vulnerability/CVE-2015-8663
Type: osv

## Details
The ff_get_buffer function in libavcodec/utils.c in FFmpeg before 2.8.4 preserves width and height values after a failure, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via a crafted .mov file.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=abee0a1c60612e8638640a8a3738fffb65e16dbf
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00004.html
- http://www.securitytracker.com/id/1034539
- https://lists.debian.org/debian-lts-announce/2018/12/msg00009.html
