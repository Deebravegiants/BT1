# [H] CVE-2017-12863

## Summary
Severity: High
Advisory: CVE-2017-12863
Aliases: GHSA-wq8f-wvqp-xvvm, PYSEC-2026-2832, PYSEC-2026-717
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-15
Source: https://osv.dev/vulnerability/CVE-2017-12863
Type: osv

## Details
In opencv/modules/imgcodecs/src/grfmt_pxm.cpp, function PxMDecoder::readData has an integer overflow when calculate src_pitch. If the image is from remote, may lead to remote code execution or denial of service. This affects Opencv 3.3 and earlier.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00030.html
- https://lists.debian.org/debian-lts-announce/2021/10/msg00028.html
- https://security.gentoo.org/glsa/201712-02
- https://github.com/opencv/opencv/issues/9371
