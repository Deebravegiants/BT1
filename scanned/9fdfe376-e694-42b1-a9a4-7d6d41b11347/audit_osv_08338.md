# [H] CVE-2016-2329

## Summary
Severity: High
Advisory: CVE-2016-2329
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-02-12
Source: https://osv.dev/vulnerability/CVE-2016-2329
Type: osv

## Details
libavcodec/tiff.c in FFmpeg before 2.8.6 does not properly validate RowsPerStrip values and YCbCr chrominance subsampling factors, which allows remote attackers to cause a denial of service (out-of-bounds array access) or possibly have unspecified other impact via a crafted TIFF file, related to the tiff_decode_tag and decode_frame functions.

## References
- http://git.videolan.org/?p=ffmpeg.git%3Ba=commit%3Bh=89f464e9c229006e16f6bb5403c5529fdd0a9edd
- http://lists.opensuse.org/opensuse-updates/2016-02/msg00129.html
- http://www.securityfocus.com/bid/84212
- http://www.securitytracker.com/id/1035010
- https://security.gentoo.org/glsa/201606-09
