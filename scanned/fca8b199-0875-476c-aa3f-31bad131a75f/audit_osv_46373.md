# [H] CVE-2007-0897

## Summary
Severity: High
Advisory: CVE-2007-0897
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2007-02-16
Source: https://osv.dev/vulnerability/CVE-2007-0897
Type: osv

## Details
Clam AntiVirus ClamAV before 0.90 does not close open file descriptors under certain conditions, which allows remote attackers to cause a denial of service (file descriptor consumption and failed scans) via CAB archives with a cabinet header record length of zero, which causes a function to return without closing a file descriptor.

## References
- http://labs.idefense.com/intelligence/vulnerabilities/display.php?id=475
- http://secunia.com/advisories/24183
- http://secunia.com/advisories/24187
- http://secunia.com/advisories/24192
- http://secunia.com/advisories/24319
- http://secunia.com/advisories/24332
- http://secunia.com/advisories/24425
- http://secunia.com/advisories/29420
- http://security.gentoo.org/glsa/glsa-200703-03.xml
- http://www.mandriva.com/security/advisories?name=MDKSA-2007:043
- http://www.securityfocus.com/bid/22580
- http://www.securitytracker.com/id?1017659
- http://www.vupen.com/english/advisories/2007/0623
- http://www.vupen.com/english/advisories/2008/0924/references
- https://exchange.xforce.ibmcloud.com/vulnerabilities/32531
- http://lists.apple.com/archives/security-announce/2008/Mar/msg00001.html
- http://www.debian.org/security/2007/dsa-1263
- http://secunia.com/advisories/24187
- http://www.securityfocus.com/bid/22580
- http://docs.info.apple.com/article.html?artnum=307562
