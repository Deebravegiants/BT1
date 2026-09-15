# [M] CVE-2016-9042

## Summary
Severity: Medium
Advisory: CVE-2016-9042
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2016-9042
Type: osv

## Details
An exploitable denial of service vulnerability exists in the origin timestamp check functionality of ntpd 4.2.8p9. A specially crafted unauthenticated network packet can be used to reset the expected origin timestamp for target peers. Legitimate replies from targeted peers will fail the origin timestamp check (TEST2) causing the reply to be dropped and creating a denial of service condition.

## References
- http://packetstormsecurity.com/files/142284/Slackware-Security-Advisory-ntp-Updates.html
- http://seclists.org/fulldisclosure/2017/Nov/7
- http://seclists.org/fulldisclosure/2017/Sep/62
- http://www.securityfocus.com/archive/1/540403/100/0/threaded
- http://www.securityfocus.com/archive/1/archive/1/540464/100/0/threaded
- http://packetstormsecurity.com/files/142101/FreeBSD-Security-Advisory-FreeBSD-SA-17-03.ntp.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7KVLFA3J43QFIP4I7HE7KQ5FXSMJEKC6/
- https://support.apple.com/kb/HT208144
- https://support.f5.com/csp/article/K39041624
- http://www.securityfocus.com/archive/1/archive/1/540403/100/0/threaded
- https://kc.mcafee.com/corporate/index?page=content&id=SB10201
- http://www.securitytracker.com/id/1039427
- http://www.ubuntu.com/usn/USN-3349-1
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03962en_us
- http://www.securitytracker.com/id/1038123
- https://cert-portal.siemens.com/productcert/pdf/ssa-211752.pdf
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:03.ntp.asc
- https://bto.bluecoat.com/security-advisory/sa147
- https://us-cert.cisa.gov/ics/advisories/icsa-21-159-11
- http://www.securityfocus.com/bid/97046
