# [M] CVE-2018-1050

## Summary
Severity: Medium
Advisory: CVE-2018-1050
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1050
Type: osv

## Details
All versions of Samba from 4.0.0 onwards are vulnerable to a denial of service attack when the RPC spoolss service is configured to be run as an external daemon. Missing input sanitization checks on some of the input parameters to spoolss RPC calls could cause the print spooler service to crash.

## References
- http://www.securityfocus.com/bid/103387
- http://www.securitytracker.com/id/1040493
- https://access.redhat.com/errata/RHSA-2018:1860
- https://access.redhat.com/errata/RHSA-2018:1883
- https://access.redhat.com/errata/RHSA-2018:2612
- https://access.redhat.com/errata/RHSA-2018:2613
- https://access.redhat.com/errata/RHSA-2018:3056
- https://help.ecostruxureit.com/display/public/UADCE725/Security+fixes+in+StruxureWare+Data+Center+Expert+v7.6.0
- https://lists.debian.org/debian-lts-announce/2018/03/msg00024.html
- https://lists.debian.org/debian-lts-announce/2019/04/msg00013.html
- https://security.gentoo.org/glsa/201805-07
- https://security.netapp.com/advisory/ntap-20180313-0001/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbns03834en_us
- https://usn.ubuntu.com/3595-1/
- https://usn.ubuntu.com/3595-2/
- https://www.debian.org/security/2018/dsa-4135
- https://www.samba.org/samba/security/CVE-2018-1050.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1538771
