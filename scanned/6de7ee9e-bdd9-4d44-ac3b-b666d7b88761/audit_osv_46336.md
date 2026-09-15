# [C] CVE-2002-0391

## Summary
Severity: Critical
Advisory: CVE-2002-0391
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2002-08-12
Source: https://osv.dev/vulnerability/CVE-2002-0391
Type: osv

## Details
Integer overflow in xdr_array function in RPC servers for operating systems that use libc, glibc, or other code based on SunRPC including dietlibc, allows remote attackers to execute arbitrary code by passing a large number of arguments to xdr_array through RPC services such as rpc.cmsd and dmispd.

## References
- ftp://ftp.netbsd.org/pub/NetBSD/security/advisories/NetBSD-SA2002-011.txt.asc
- ftp://patches.sgi.com/support/free/security/advisories/20020801-01-A
- ftp://patches.sgi.com/support/free/security/advisories/20020801-01-P
- http://bvlive01.iss.net/issEn/delivery/xforce/alertdetail.jsp?oid=20823
- http://online.securityfocus.com/advisories/4402
- http://online.securityfocus.com/archive/1/285740
- http://rhn.redhat.com/errata/RHSA-2002-166.html
- http://rhn.redhat.com/errata/RHSA-2002-172.html
- http://www.cert.org/advisories/CA-2002-25.html
- http://www.debian.org/security/2002/dsa-142
- http://www.debian.org/security/2002/dsa-143
- http://www.debian.org/security/2002/dsa-146
- http://www.debian.org/security/2002/dsa-149
- http://www.debian.org/security/2003/dsa-333
- http://www.kb.cert.org/vuls/id/192995
- http://www.linuxsecurity.com/advisories/other_advisory-2399.html
- http://www.mandrakesoft.com/security/advisories?name=MDKSA-2002:057
- http://www.securityfocus.com/bid/5356
- https://docs.microsoft.com/en-us/security-updates/securitybulletins/2002/ms02-057
- http://marc.info/?l=bugtraq&m=102813809232532&w=2
