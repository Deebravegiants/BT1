# [H] CVE-2015-7974

## Summary
Severity: High
Advisory: CVE-2015-7974
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)
Published: 2016-01-26
Source: https://osv.dev/vulnerability/CVE-2015-7974
Type: osv

## Details
NTP 4.x before 4.2.8p6 and 4.3.x before 4.3.90 do not verify peer associations of symmetric keys when authenticating packets, which might allow remote attackers to conduct impersonation attacks via an arbitrary trusted key, aka a "skeleton key."

## References
- http://bugs.ntp.org/show_bug.cgi?id=2936
- http://rhn.redhat.com/errata/RHSA-2016-2583.html
- http://support.ntp.org/bin/view/Main/NtpBug2936
- http://www.debian.org/security/2016/dsa-3629
- http://www.securityfocus.com/bid/81960
- http://www.securitytracker.com/id/1034782
- http://www.talosintel.com/reports/TALOS-2016-0071/
- https://cert-portal.siemens.com/productcert/pdf/ssa-497656.pdf
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03750en_us
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03766en_us
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:09.ntp.asc
- https://security.gentoo.org/glsa/201607-15
- https://security.netapp.com/advisory/ntap-20171031-0001/
- https://us-cert.cisa.gov/ics/advisories/icsa-21-103-11
- http://www.talosintel.com/reports/TALOS-2016-0071/
- http://bugs.ntp.org/show_bug.cgi?id=2936
