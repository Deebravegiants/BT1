# [H] CVE-2018-15822

## Summary
Severity: High
Advisory: CVE-2018-15822
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-23
Source: https://osv.dev/vulnerability/CVE-2018-15822
Type: osv

## Details
The flv_write_packet function in libavformat/flvenc.c in FFmpeg through 2.8 does not check for an empty audio packet, leading to an assertion failure.

## References
- https://lists.debian.org/debian-lts-announce/2019/05/msg00043.html
- https://seclists.org/bugtraq/2019/May/60
- https://usn.ubuntu.com/3967-1/
- https://usn.ubuntu.com/4431-1/
- https://www.debian.org/security/2019/dsa-4449
- https://github.com/FFmpeg/FFmpeg/commit/6b67d7f05918f7a1ee8fc6ff21355d7e8736aa10
- https://github.com/FFmpeg/FFmpeg/commit/d8ecb335fe4852bbc172c7b79e66944d158b4d92
