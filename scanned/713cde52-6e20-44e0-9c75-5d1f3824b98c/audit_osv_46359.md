# [M] CVE-2005-1111

## Summary
Severity: Medium
Advisory: CVE-2005-1111
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2005-05-02
Source: https://osv.dev/vulnerability/CVE-2005-1111
Type: osv

## Details
Race condition in cpio 2.6 and earlier allows local users to modify permissions of arbitrary files via a hard link attack on a file while it is being decompressed, whose permissions are changed by cpio after the decompression is complete.

## References
- ftp://ftp.freebsd.org/pub/FreeBSD/CERT/advisories/FreeBSD-SA-06:03.cpio.asc
- http://secunia.com/advisories/16998
- http://secunia.com/advisories/17123
- http://secunia.com/advisories/17532
- http://secunia.com/advisories/18290
- http://secunia.com/advisories/18395
- http://secunia.com/advisories/20117
- http://www.debian.org/security/2005/dsa-846
- http://www.securityfocus.com/bid/13159
- http://www.ubuntu.com/usn/usn-189-1
- http://marc.info/?l=bugtraq&m=111342664116120&w=2
- ftp://ftp.sco.com/pub/updates/OpenServer/SCOSA-2006.2/SCOSA-2006.2.txt
- ftp://ftp.sco.com/pub/updates/UnixWare/SCOSA-2005.32/SCOSA-2005.32.txt
- http://lists.suse.com/archive/suse-security-announce/2006-May/0004.html
- http://www.osvdb.org/15725
- http://www.redhat.com/support/errata/RHSA-2005-378.html
- http://www.redhat.com/support/errata/RHSA-2005-806.html
- http://www.securityfocus.com/bid/13159
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A358
- https://oval.cisecurity.org/repository/search/definition/oval%3Aorg.mitre.oval%3Adef%3A9783
