# [H] CVE-2017-12864

## Summary
Severity: High
Advisory: CVE-2017-12864
Aliases: GHSA-267x-w5hx-8hjr, PYSEC-2026-2804, PYSEC-2026-697
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-15
Source: https://osv.dev/vulnerability/CVE-2017-12864
Type: osv

## Details
In opencv/modules/imgcodecs/src/grfmt_pxm.cpp, function ReadNumber did not checkout the input length, which lead to integer overflow. If the image is from remote, may lead to remote code execution or denial of service. This affects Opencv 3.3 and earlier.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9372
