# [M] CVE-2017-7593

## Summary
Severity: Medium
Advisory: CVE-2017-7593
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-04-09
Source: https://osv.dev/vulnerability/CVE-2017-7593
Type: osv

## Details
tif_read.c in LibTIFF 4.0.7 does not ensure that tif_rawdata is properly initialized, which might allow remote attackers to obtain sensitive information from process memory via a crafted image.

## References
- https://usn.ubuntu.com/3602-1/
- http://www.debian.org/security/2017/dsa-3844
- http://www.securityfocus.com/bid/97502
- https://security.gentoo.org/glsa/201709-27
- http://bugzilla.maptools.org/show_bug.cgi?id=2651
