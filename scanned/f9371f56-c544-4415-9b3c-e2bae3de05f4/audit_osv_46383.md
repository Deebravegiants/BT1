# [M] CVE-2008-1447

## Summary
Severity: Medium
Advisory: CVE-2008-1447
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2008-07-08
Source: https://osv.dev/vulnerability/CVE-2008-1447
Type: osv

## Details
The DNS protocol, as implemented in (1) BIND 8 and 9 before 9.5.0-P1, 9.4.2-P1, and 9.3.5-P1; (2) Microsoft DNS in Windows 2000 SP4, XP SP2 and SP3, and Server 2003 SP1 and SP2; and other implementations allow remote attackers to spoof DNS traffic via a birthday attack that uses in-bailiwick referrals to conduct cache poisoning against recursive resolvers, related to insufficient randomness of DNS transaction IDs and source ports, aka "DNS Insufficient Socket Entropy Vulnerability" or "the Kaminsky bug."

## References
- ftp://ftp.netbsd.org/pub/NetBSD/security/advisories/NetBSD-SA2008-009.txt.asc
- http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=494401
- http://lists.apple.com/archives/security-announce//2008/Jul/msg00003.html
- http://lists.apple.com/archives/security-announce//2008/Sep/msg00003.html
- http://lists.apple.com/archives/security-announce//2008/Sep/msg00004.html
- http://lists.apple.com/archives/security-announce//2008/Sep/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2008-07/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2008-08/msg00006.html
- http://marc.info/?l=bugtraq&m=121630706004256&w=2
- http://marc.info/?l=bugtraq&m=121866517322103&w=2
- http://marc.info/?l=bugtraq&m=123324863916385&w=2
- http://marc.info/?l=bugtraq&m=141879471518471&w=2
- http://rhn.redhat.com/errata/RHSA-2008-0533.html
- http://secunia.com/advisories/30925
- http://secunia.com/advisories/30973
- http://secunia.com/advisories/30977
- http://secunia.com/advisories/30979
- http://secunia.com/advisories/30980
- http://secunia.com/advisories/30988
- http://secunia.com/advisories/30989
