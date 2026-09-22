# [H] CVE-2016-2776

## Summary
Severity: High
Advisory: CVE-2016-2776
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-28
Source: https://osv.dev/vulnerability/CVE-2016-2776
Type: osv

## Details
buffer.c in named in ISC BIND 9 before 9.9.9-P3, 9.10.x before 9.10.4-P3, and 9.11.x before 9.11.0rc3 does not properly construct responses, which allows remote attackers to cause a denial of service (assertion failure and daemon exit) via a crafted query.

## References
- http://www.securityfocus.com/bid/93188
- http://www.securitytracker.com/id/1036903
- https://kb.isc.org/article/AA-01435
- https://kb.isc.org/article/AA-01436
- https://kb.isc.org/article/AA-01438
- https://www.exploit-db.com/exploits/40453/
- http://rhn.redhat.com/errata/RHSA-2016-1944.html
- http://rhn.redhat.com/errata/RHSA-2016-1945.html
- http://rhn.redhat.com/errata/RHSA-2016-2099.html
- http://www.oracle.com/technetwork/topics/security/bulletinoct2016-3090566.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05321107
- https://kb.isc.org/article/AA-01419/0
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:28.bind.asc
- https://security.gentoo.org/glsa/201610-07
- https://security.netapp.com/advisory/ntap-20160930-0001/
