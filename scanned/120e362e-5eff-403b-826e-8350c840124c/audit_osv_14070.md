# [M] CVE-2018-6912

## Summary
Severity: Medium
Advisory: CVE-2018-6912
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2018-6912
Type: osv

## Details
The decode_plane function in libavcodec/utvideodec.c in FFmpeg through 3.4.2 allows remote attackers to cause a denial of service (out of array read) via a crafted AVI file.

## References
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/76cc0f0f673353cd4746cd3b83838ae335e5d9ed
- https://security.gentoo.org/glsa/202003-65
