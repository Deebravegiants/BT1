# [H] CVE-2016-7502

## Summary
Severity: High
Advisory: CVE-2016-7502
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-7502
Type: osv

## Details
The cavs_idct8_add_c function in libavcodec/cavsdsp.c in FFmpeg before 3.1.4 is vulnerable to reading out-of-bounds memory when decoding with cavs_decode.

## References
- http://www.openwall.com/lists/oss-security/2016/10/08/1
- http://www.securityfocus.com/bid/94834
- https://security.gentoo.org/glsa/201701-71
