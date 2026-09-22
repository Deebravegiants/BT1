# [C] CVE-2004-0434

## Summary
Severity: Critical
Advisory: CVE-2004-0434
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2004-07-07
Source: https://osv.dev/vulnerability/CVE-2004-0434
Type: osv

## Details
k5admind (kadmind) for Heimdal allows remote attackers to execute arbitrary code via a Kerberos 4 compatibility administration request whose framing length is less than 2, which leads to a heap-based buffer overflow.

## References
- ftp://ftp.freebsd.org/pub/FreeBSD/CERT/advisories/FreeBSD-SA-04:09.kadmind.asc
- http://lists.grok.org.uk/pipermail/full-disclosure/2004-May/020998.html
- http://security.gentoo.org/glsa/glsa-200405-23.xml
- http://www.debian.org/security/2004/dsa-504
- https://exchange.xforce.ibmcloud.com/vulnerabilities/16071
- http://marc.info/?l=bugtraq&m=108386148126457&w=2
- http://www.debian.org/security/2004/dsa-504
- http://lists.grok.org.uk/pipermail/full-disclosure/2004-May/020998.html
