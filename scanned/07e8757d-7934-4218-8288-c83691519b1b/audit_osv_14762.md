# [H] CVE-2019-11338

## Summary
Severity: High
Advisory: CVE-2019-11338
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-04-19
Source: https://osv.dev/vulnerability/CVE-2019-11338
Type: osv

## Details
libavcodec/hevcdec.c in FFmpeg 3.4 and 4.1.2 mishandles detection of duplicate first slices, which allows remote attackers to cause a denial of service (NULL pointer dereference and out-of-array access) or possibly have unspecified other impact via crafted HEVC data.

## References
- http://www.securityfocus.com/bid/108034
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00012.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00043.html
- https://seclists.org/bugtraq/2019/May/60
- https://usn.ubuntu.com/3967-1/
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2019/dsa-4449
- https://github.com/FFmpeg/FFmpeg/commit/54655623a82632e7624714d7b2a3e039dc5faa7e
- https://github.com/FFmpeg/FFmpeg/commit/9ccc633068c6fe76989f487c8932bd11886ad65b
