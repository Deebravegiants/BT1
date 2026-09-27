# [H] CVE-2017-12150

## Summary
Severity: High
Advisory: CVE-2017-12150
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-12150
Type: osv

## Details
It was found that samba before 4.4.16, 4.5.x before 4.5.14, and 4.6.x before 4.6.8 did not enforce "SMB signing" when certain configuration options were enabled. A remote attacker could launch a man-in-the-middle attack and retrieve information in plain-text.

## References
- http://www.securityfocus.com/bid/100918
- http://www.securitytracker.com/id/1039401
- https://access.redhat.com/errata/RHSA-2017:2789
- https://access.redhat.com/errata/RHSA-2017:2790
- https://access.redhat.com/errata/RHSA-2017:2791
- https://access.redhat.com/errata/RHSA-2017:2858
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbns03775en_us
- https://security.netapp.com/advisory/ntap-20170921-0001/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03817en_us
- https://www.debian.org/security/2017/dsa-3983
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12150
- https://www.samba.org/samba/security/CVE-2017-12150.html
