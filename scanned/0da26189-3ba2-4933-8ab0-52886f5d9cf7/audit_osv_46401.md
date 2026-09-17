# [H] CVE-2009-1955

## Summary
Severity: High
Advisory: CVE-2009-1955
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2009-06-08
Source: https://osv.dev/vulnerability/CVE-2009-1955
Type: osv

## Details
The expat XML parser in the apr_xml_* interface in xml/apr_xml.c in Apache APR-util before 1.3.7, as used in the mod_dav and mod_dav_svn modules in the Apache HTTP Server, allows remote attackers to cause a denial of service (memory consumption) via a crafted XML document containing a large number of nested entity references, as demonstrated by a PROPFIND request, a similar issue to CVE-2003-1564.

## References
- http://lists.apple.com/archives/security-announce/2009/Nov/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2010-05/msg00001.html
- http://secunia.com/advisories/34724
- http://secunia.com/advisories/35284
- http://secunia.com/advisories/35360
- http://secunia.com/advisories/35395
- http://secunia.com/advisories/35444
- http://secunia.com/advisories/35487
- http://secunia.com/advisories/35565
- http://secunia.com/advisories/35710
- http://secunia.com/advisories/35797
- http://secunia.com/advisories/35843
- http://secunia.com/advisories/36473
- http://secunia.com/advisories/37221
- http://security.gentoo.org/glsa/glsa-200907-03.xml
- http://slackware.com/security/viewer.php?l=slackware-security&y=2009&m=slackware-security.538210
- http://www-01.ibm.com/support/docview.wss?uid=swg1PK91241
- http://www-01.ibm.com/support/docview.wss?uid=swg1PK99478
- http://www-01.ibm.com/support/docview.wss?uid=swg27014463
- http://www.debian.org/security/2009/dsa-1812
