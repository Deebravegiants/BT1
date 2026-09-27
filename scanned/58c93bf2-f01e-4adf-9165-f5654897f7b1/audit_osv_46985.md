# [H] CVE-2015-8662

## Summary
Severity: High
Advisory: CVE-2015-8662
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2015-12-24
Source: https://osv.dev/vulnerability/CVE-2015-8662
Type: osv

## Details
The ff_dwt_decode function in libavcodec/jpeg2000dwt.c in FFmpeg before 2.8.4 does not validate the number of decomposition levels before proceeding with Discrete Wavelet Transform decoding, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via crafted JPEG 2000 data.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=75422280fbcdfbe9dc56bde5525b4d8b280f1bc5
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00004.html
- http://www.securitytracker.com/id/1034539
- https://lists.debian.org/debian-lts-announce/2018/12/msg00009.html
