# [H] CVE-2017-12862

## Summary
Severity: High
Advisory: CVE-2017-12862
Aliases: GHSA-5rpc-gwh9-q9fg, PYSEC-2026-2807, PYSEC-2026-699
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-15
Source: https://osv.dev/vulnerability/CVE-2017-12862
Type: osv

## Details
In modules/imgcodecs/src/grfmt_pxm.cpp, the length of buffer AutoBuffer _src is small than expected, which will cause copy buffer overflow later. If the image is from remote, may lead to remote code execution or denial of service. This affects Opencv 3.3 and earlier.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9370
