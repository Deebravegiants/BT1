# [M] CVE-2018-15607

## Summary
Severity: Medium
Advisory: CVE-2018-15607
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-08-21
Source: https://osv.dev/vulnerability/CVE-2018-15607
Type: osv

## Details
In ImageMagick 7.0.8-11 Q16, a tiny input file 0x50 0x36 0x36 0x36 0x36 0x4c 0x36 0x38 0x36 0x36 0x36 0x36 0x36 0x36 0x1f 0x35 0x50 0x00 can result in a hang of several minutes during which CPU and memory resources are consumed until ultimately an attempted large memory allocation fails. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted file.

## References
- https://usn.ubuntu.com/4034-1/
- http://www.securityfocus.com/bid/105137
- https://github.com/ImageMagick/ImageMagick/issues/1255
