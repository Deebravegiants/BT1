# [H] CVE-2016-8864

## Summary
Severity: High
Advisory: CVE-2016-8864
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-02
Source: https://osv.dev/vulnerability/CVE-2016-8864
Type: osv

## Details
named in ISC BIND 9.x before 9.9.9-P4, 9.10.x before 9.10.4-P4, and 9.11.x before 9.11.0-P1 allows remote attackers to cause a denial of service (assertion failure and daemon exit) via a DNAME record in the answer section of a response to a recursive query, related to db.c and resolver.c.

## References
- https://kb.isc.org/article/AA-01435
- https://kb.isc.org/article/AA-01436
- https://kb.isc.org/article/AA-01437
- https://kb.isc.org/article/AA-01438
- http://rhn.redhat.com/errata/RHSA-2016-2141.html
- http://rhn.redhat.com/errata/RHSA-2016-2142.html
- http://rhn.redhat.com/errata/RHSA-2016-2615.html
- http://rhn.redhat.com/errata/RHSA-2016-2871.html
- http://www.debian.org/security/2016/dsa-3703
- http://www.securityfocus.com/bid/94067
- http://www.securitytracker.com/id/1037156
- https://access.redhat.com/errata/RHSA-2017:1583
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05381687
- https://kb.isc.org/article/AA-01434
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:34.bind.asc
- https://security.gentoo.org/glsa/201701-26
- https://security.netapp.com/advisory/ntap-20180926-0005/
