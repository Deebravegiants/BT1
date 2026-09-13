# [M] CVE-2016-7555

## Summary
Severity: Medium
Advisory: CVE-2016-7555
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-7555
Type: osv

## Details
The avi_read_header function in libavformat/avidec.c in FFmpeg before 3.1.4 is vulnerable to memory leak when decoding an AVI file that has a crafted "strh" structure.

## References
- http://www.openwall.com/lists/oss-security/2016/10/08/1
- http://www.securityfocus.com/bid/94838
- https://security.gentoo.org/glsa/201701-71
