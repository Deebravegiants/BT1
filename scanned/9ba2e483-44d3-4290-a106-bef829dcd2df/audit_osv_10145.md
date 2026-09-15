# [M] CVE-2017-14055

## Summary
Severity: Medium
Advisory: CVE-2017-14055
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-31
Source: https://osv.dev/vulnerability/CVE-2017-14055
Type: osv

## Details
In libavformat/mvdec.c in FFmpeg 3.3.3, a DoS in mv_read_header() due to lack of an EOF (End of File) check might cause huge CPU and memory consumption. When a crafted MV file, which claims a large "nb_frames" field in the header but does not contain sufficient backing data, is provided, the loop over the frames would consume huge CPU and memory resources, since there is no EOF check inside the loop.

## References
- http://www.securityfocus.com/bid/100626
- https://lists.debian.org/debian-lts-announce/2019/01/msg00006.html
- http://www.debian.org/security/2017/dsa-3996
- https://github.com/FFmpeg/FFmpeg/commit/4f05e2e2dc1a89f38cd9f0960a6561083d714f1e
