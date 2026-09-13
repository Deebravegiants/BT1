# [H] CVE-2016-2326

## Summary
Severity: High
Advisory: CVE-2016-2326
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/CVE-2016-2326
Type: osv

## Details
Integer overflow in the asf_write_packet function in libavformat/asfenc.c in FFmpeg before 2.8.5 allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted PTS (aka presentation timestamp) value in a .mov file.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=7c0b84d89911b2035161f5ef51aafbfcc84aa9e2
- http://www.debian.org/security/2016/dsa-3506
- http://www.securityfocus.com/bid/84165
- http://www.securitytracker.com/id/1035010
- http://www.ubuntu.com/usn/USN-2944-1
- https://security.gentoo.org/glsa/201606-09
- https://security.gentoo.org/glsa/201705-08
