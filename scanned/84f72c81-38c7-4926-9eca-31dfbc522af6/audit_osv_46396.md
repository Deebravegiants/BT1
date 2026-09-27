# [H] CVE-2009-0949

## Summary
Severity: High
Advisory: CVE-2009-0949
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2009-06-09
Source: https://osv.dev/vulnerability/CVE-2009-0949
Type: osv

## Details
The ippReadIO function in cups/ipp.c in cupsd in CUPS before 1.3.10 does not properly initialize memory for IPP request packets, which allows remote attackers to cause a denial of service (NULL pointer dereference and daemon crash) via a scheduler request with two consecutive IPP_TAG_UNSUPPORTED tags.

## References
- http://secunia.com/advisories/35322
- http://secunia.com/advisories/35328
- http://secunia.com/advisories/35340
- http://secunia.com/advisories/35342
- http://secunia.com/advisories/35685
- http://secunia.com/advisories/36701
- http://securitytracker.com/id?1022321
- http://support.apple.com/kb/HT3865
- http://www.coresecurity.com/content/AppleCUPS-null-pointer-vulnerability
- http://www.debian.org/security/2009/dsa-1811
- http://www.securityfocus.com/archive/1/504032/100/0/threaded
- http://www.securityfocus.com/bid/35169
- http://www.ubuntu.com/usn/USN-780-1
- https://exchange.xforce.ibmcloud.com/vulnerabilities/50926
- http://lists.apple.com/archives/security-announce/2009/Sep/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2009-07/msg00002.html
- http://www.coresecurity.com/content/AppleCUPS-null-pointer-vulnerability
- http://www.securityfocus.com/bid/35169
- https://bugzilla.redhat.com/show_bug.cgi?id=500972
- http://securitytracker.com/id?1022321
