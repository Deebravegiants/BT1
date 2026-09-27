# [C] CVE-2016-0729

## Summary
Severity: Critical
Advisory: CVE-2016-0729
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-0729
Type: osv

## Details
Multiple buffer overflows in (1) internal/XMLReader.cpp, (2) util/XMLURL.cpp, and (3) util/XMLUri.cpp in the XML Parser library in Apache Xerces-C before 3.1.3 allow remote attackers to cause a denial of service (segmentation fault or memory corruption) or possibly execute arbitrary code via a crafted document.

## References
- http://www.securitytracker.com/id/1035113
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00053.html
- http://packetstormsecurity.com/files/135949/Apache-Xerces-C-XML-Parser-Buffer-Overflow.html
- http://svn.apache.org/viewvc?view=revision&revision=1727978
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00086.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/archive/1/537620/100/0/threaded
- http://www.securityfocus.com/bid/83423
- http://lists.opensuse.org/opensuse-updates/2016-04/msg00012.html
- http://xerces.apache.org/xerces-c/secadv/CVE-2016-0729.txt
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182131.html
- http://www.debian.org/security/2016/dsa-3493
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182597.html
- https://security.gentoo.org/glsa/201612-46
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182062.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- https://issues.apache.org/jira/browse/XERCESC-2061
