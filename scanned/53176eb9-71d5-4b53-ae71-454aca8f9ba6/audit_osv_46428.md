# [C] CVE-2010-2941

## Summary
Severity: Critical
Advisory: CVE-2010-2941
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2010-11-05
Source: https://osv.dev/vulnerability/CVE-2010-2941
Type: osv

## Details
ipp.c in cupsd in CUPS 1.4.4 and earlier does not properly allocate memory for attribute values with invalid string data types, which allows remote attackers to cause a denial of service (use-after-free and application crash) or possibly execute arbitrary code via a crafted IPP request.

## References
- http://rhn.redhat.com/errata/RHSA-2010-0811.html
- http://secunia.com/advisories/42287
- http://secunia.com/advisories/42867
- http://secunia.com/advisories/43521
- http://security.gentoo.org/glsa/glsa-201207-10.xml
- http://securitytracker.com/id?1024662
- http://www.debian.org/security/2011/dsa-2176
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:232
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:233
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:234
- http://www.securityfocus.com/bid/44530
- http://www.ubuntu.com/usn/USN-1012-1
- http://www.vupen.com/english/advisories/2010/2856
- http://www.vupen.com/english/advisories/2010/3042
- http://www.vupen.com/english/advisories/2010/3088
- http://www.vupen.com/english/advisories/2011/0061
- http://www.vupen.com/english/advisories/2011/0535
- https://exchange.xforce.ibmcloud.com/vulnerabilities/62882
- http://blogs.sun.com/security/entry/multiple_vulnerabilities_in_mozilla_firefox
- http://lists.apple.com/archives/security-announce/2010//Nov/msg00000.html
