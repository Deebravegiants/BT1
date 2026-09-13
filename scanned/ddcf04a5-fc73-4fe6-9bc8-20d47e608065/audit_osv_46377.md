# [H] CVE-2007-4988

## Summary
Severity: High
Advisory: CVE-2007-4988
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2007-09-24
Source: https://osv.dev/vulnerability/CVE-2007-4988
Type: osv

## Details
Sign extension error in the ReadDIBImage function in ImageMagick before 6.3.5-9 allows context-dependent attackers to execute arbitrary code via a crafted width value in an image file, which triggers an integer overflow and a heap-based buffer overflow.

## References
- http://secunia.com/advisories/26926
- http://secunia.com/advisories/27048
- http://secunia.com/advisories/27309
- http://secunia.com/advisories/27364
- http://secunia.com/advisories/27439
- http://secunia.com/advisories/28721
- http://secunia.com/advisories/29786
- http://secunia.com/advisories/36260
- http://security.gentoo.org/glsa/glsa-200710-27.xml
- http://www.debian.org/security/2009/dsa-1858
- http://www.imagemagick.org/script/changelog.php
- http://www.mandriva.com/en/security/advisories?name=MDVSA-2008:035
- http://www.novell.com/linux/security/advisories/2007_23_sr.html
- http://www.securityfocus.com/archive/1/483572/100/0/threaded
- http://www.securityfocus.com/bid/25765
- http://www.securitytracker.com/id?1018729
- http://www.ubuntu.com/usn/usn-523-1
- http://www.vupen.com/english/advisories/2007/3245
- https://exchange.xforce.ibmcloud.com/vulnerabilities/36737
- http://www.debian.org/security/2009/dsa-1858
