# [H] CVE-2016-7450

## Summary
Severity: High
Advisory: CVE-2016-7450
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-7450
Type: osv

## Details
The ff_log2_16bit_c function in libavutil/intmath.h in FFmpeg before 3.1.4 is vulnerable to reading out-of-bounds memory when it decodes a malformed AIFF file.

## References
- http://www.openwall.com/lists/oss-security/2016/10/08/1
- http://www.securityfocus.com/bid/94841
- https://security.gentoo.org/glsa/201701-71
