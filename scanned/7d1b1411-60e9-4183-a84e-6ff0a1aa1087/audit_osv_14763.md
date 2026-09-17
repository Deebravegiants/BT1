# [H] CVE-2019-11339

## Summary
Severity: High
Advisory: CVE-2019-11339
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-19
Source: https://osv.dev/vulnerability/CVE-2019-11339
Type: osv

## Details
The studio profile decoder in libavcodec/mpeg4videodec.c in FFmpeg 4.0 before 4.0.4 and 4.1 before 4.1.2 allows remote attackers to cause a denial of service (out-of-array access) or possibly have unspecified other impact via crafted MPEG-4 video data.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00012.html
- https://usn.ubuntu.com/3967-1/
- http://www.securityfocus.com/bid/108037
- https://github.com/FFmpeg/FFmpeg/commit/1f686d023b95219db933394a7704ad9aa5f01cbb
- https://github.com/FFmpeg/FFmpeg/commit/d227ed5d598340e719eff7156b1aa0a4469e9a6a
