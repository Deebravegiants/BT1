# [M] CVE-2010-0629

## Summary
Severity: Medium
Advisory: CVE-2010-0629
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2010-04-07
Source: https://osv.dev/vulnerability/CVE-2010-0629
Type: osv

## Details
Use-after-free vulnerability in kadmin/server/server_stubs.c in kadmind in MIT Kerberos 5 (aka krb5) 1.5 through 1.6.3 allows remote authenticated users to cause a denial of service (daemon crash) via a request from a kadmin client that sends an invalid API version number.

## References
- http://krbdev.mit.edu/rt/Ticket/Display.html?id=5998
- http://secunia.com/advisories/39264
- http://secunia.com/advisories/39290
- http://secunia.com/advisories/39315
- http://secunia.com/advisories/39324
- http://secunia.com/advisories/39367
- http://securitytracker.com/id?1023821
- http://ubuntu.com/usn/usn-924-1
- http://web.mit.edu/kerberos/advisories/MITKRB5-SA-2010-003.txt
- http://www.mandriva.com/security/advisories?name=MDVSA-2010:071
- http://www.securityfocus.com/archive/1/510566/100/0/threaded
- http://www.securityfocus.com/bid/39247
- http://www.vupen.com/english/advisories/2010/0876
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=567052
- http://lists.fedoraproject.org/pipermail/package-announce/2010-April/038556.html
- http://lists.opensuse.org/opensuse-security-announce/2010-04/msg00002.html
- http://www.debian.org/security/2010/dsa-2031
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=567052
- http://web.mit.edu/kerberos/advisories/MITKRB5-SA-2010-003.txt
- http://www.securityfocus.com/bid/39247
