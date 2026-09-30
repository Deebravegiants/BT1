# [M] CVE-2018-7557

## Summary
Severity: Medium
Advisory: CVE-2018-7557
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-28
Source: https://osv.dev/vulnerability/CVE-2018-7557
Type: osv

## Details
The decode_init function in libavcodec/utvideodec.c in FFmpeg 2.8 through 3.4.2 allows remote attackers to cause a denial of service (Out of array read) via an AVI file with crafted dimensions within chroma subsampling data.

## References
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- https://security.gentoo.org/glsa/202003-65
- https://www.debian.org/security/2018/dsa-4249
- https://git.ffmpeg.org/gitweb/ffmpeg.git/commit/7414d0bda7763f9bd69c26c068e482ab297c1c96
- https://github.com/FFmpeg/FFmpeg/commit/e724bd1dd9efea3abb8586d6644ec07694afceae
