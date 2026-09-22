# [M] CVE-2016-2213

## Summary
Severity: Medium
Advisory: CVE-2016-2213
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-02-03
Source: https://osv.dev/vulnerability/CVE-2016-2213
Type: osv

## Details
The jpeg2000_decode_tile function in libavcodec/jpeg2000dec.c in FFmpeg before 2.8.6 allows remote attackers to cause a denial of service (out-of-bounds array read access) via crafted JPEG 2000 data.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=0aada30510d809bccfd539a90ea37b61188f2cb4
- http://www.securitytracker.com/id/1034923
- https://security.gentoo.org/glsa/201606-09
