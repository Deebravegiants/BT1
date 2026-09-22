# [H] CVE-2015-5219

## Summary
Severity: High
Advisory: CVE-2015-5219
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-21
Source: https://osv.dev/vulnerability/CVE-2015-5219
Type: osv

## Details
The ULOGTOD function in ntp.d in SNTP before 4.2.7p366 does not properly perform type conversions from a precision value to a double, which allows remote attackers to cause a denial of service (infinite loop) via a crafted NTP packet.

## References
- http://aix.software.ibm.com/aix/efixes/security/ntp_advisory4.asc
- http://bk1.ntp.org/ntp-dev/?PAGE=patch&REV=51786731Gr4-NOrTBC_a_uXO4wuGhg
- http://lists.fedoraproject.org/pipermail/package-announce/2015-November/170926.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-October/169167.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166992.html
- http://rhn.redhat.com/errata/RHSA-2016-0780.html
- http://rhn.redhat.com/errata/RHSA-2016-2583.html
- http://www.debian.org/security/2015/dsa-3388
- http://www.openwall.com/lists/oss-security/2015/08/25/3
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/76473
- http://www.ubuntu.com/usn/USN-2783-1
- https://cert-portal.siemens.com/productcert/pdf/ssa-497656.pdf
- https://github.com/ntp-project/ntp/commit/5f295cd05c3c136d39f5b3e500a2d781bdbb59c8
- https://us-cert.cisa.gov/ics/advisories/icsa-21-103-11
- https://www-01.ibm.com/support/docview.wss?uid=isg3T1024157
- https://www-01.ibm.com/support/docview.wss?uid=swg21985122
- https://www-01.ibm.com/support/docview.wss?uid=swg21986956
- https://www-01.ibm.com/support/docview.wss?uid=swg21988706
- https://www-01.ibm.com/support/docview.wss?uid=swg21989542
