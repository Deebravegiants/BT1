# [H] CVE-2009-0749

## Summary
Severity: High
Advisory: CVE-2009-0749
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2009-03-02
Source: https://osv.dev/vulnerability/CVE-2009-0749
Type: osv

## Details
Use-after-free vulnerability in the GIFReadNextExtension function in lib/pngxtern/gif/gifread.c in OptiPNG 0.6.2 and earlier allows context-dependent attackers to cause a denial of service (application crash) via a crafted GIF image that causes the realloc function to return a new pointer, which triggers memory corruption when the old pointer is accessed.

## References
- http://secunia.com/advisories/34035
- http://secunia.com/advisories/34201
- http://secunia.com/advisories/34259
- http://secunia.com/advisories/35685
- http://www.gentoo.org/security/en/glsa/glsa-200903-12.xml
- http://www.securityfocus.com/bid/33873
- http://www.vupen.com/english/advisories/2009/0510
- https://exchange.xforce.ibmcloud.com/vulnerabilities/48879
- http://lists.opensuse.org/opensuse-security-announce/2009-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2009-07/msg00002.html
- http://www.openwall.com/lists/oss-security/2009/02/24/2
- http://www.openwall.com/lists/oss-security/2009/02/25/4
- http://www.securityfocus.com/bid/33873
- http://www.vupen.com/english/advisories/2009/0510
- http://sourceforge.net/tracker/index.php?func=detail&aid=2582013&group_id=151404&atid=780913
- http://optipng.sourceforge.net
- http://www.securityfocus.com/bid/33873
