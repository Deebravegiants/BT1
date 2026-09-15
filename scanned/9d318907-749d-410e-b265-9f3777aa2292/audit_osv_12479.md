# [M] CVE-2018-12458

## Summary
Severity: Medium
Advisory: CVE-2018-12458
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-06-15
Source: https://osv.dev/vulnerability/CVE-2018-12458
Type: osv

## Details
An improper integer type in the mpeg4_encode_gop_header function in libavcodec/mpeg4videoenc.c in FFmpeg 2.8 and 4.0 may trigger an assertion violation while converting a crafted AVI file to MPEG4, leading to a denial of service.

## References
- https://www.debian.org/security/2018/dsa-4249
- https://github.com/FFmpeg/FFmpeg/commit/6bbef938839adc55e8e048bc9cc2e0fafe2064df
- https://github.com/FFmpeg/FFmpeg/commit/e1182fac1afba92a4975917823a5f644bee7e6e8
