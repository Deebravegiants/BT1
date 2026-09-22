# [M] CVE-2017-14223

## Summary
Severity: Medium
Advisory: CVE-2017-14223
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-09
Source: https://osv.dev/vulnerability/CVE-2017-14223
Type: osv

## Details
In libavformat/asfdec_f.c in FFmpeg 3.3.3, a DoS in asf_build_simple_index() due to lack of an EOF (End of File) check might cause huge CPU consumption. When a crafted ASF file, which claims a large "ict" field in the header but does not contain sufficient backing data, is provided, the for loop would consume huge CPU and memory resources, since there is no EOF check inside the loop.

## References
- http://www.debian.org/security/2017/dsa-3996
- http://www.securityfocus.com/bid/100703
- https://lists.debian.org/debian-lts-announce/2019/02/msg00005.html
- https://github.com/FFmpeg/FFmpeg/commit/afc9c683ed9db01edb357bc8c19edad4282b3a97
