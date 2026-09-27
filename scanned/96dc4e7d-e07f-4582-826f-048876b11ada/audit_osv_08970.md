# [M] CVE-2016-7122

## Summary
Severity: Medium
Advisory: CVE-2016-7122
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2016-12-23
Source: https://osv.dev/vulnerability/CVE-2016-7122
Type: osv

## Details
The avi_read_nikon function in libavformat/avidec.c in FFmpeg before 3.1.4 is vulnerable to infinite loop when it decodes an AVI file that has a crafted 'nctg' structure.

## References
- http://www.securityfocus.com/bid/94839
- http://www.openwall.com/lists/oss-security/2016/10/08/1
- https://security.gentoo.org/glsa/201701-71
