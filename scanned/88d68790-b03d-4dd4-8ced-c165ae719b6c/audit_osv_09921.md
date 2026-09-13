# [H] CVE-2017-12163

## Summary
Severity: High
Advisory: CVE-2017-12163
CVSS: 7.1 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2017-12163
Type: osv

## Details
An information leak flaw was found in the way SMB1 protocol was implemented by Samba before 4.4.16, 4.5.x before 4.5.14, and 4.6.x before 4.6.8. A malicious client could use this flaw to dump server memory contents to a file on the samba share or to a shared printer, though the exact area of server memory cannot be controlled by the attacker.

## References
- http://www.securityfocus.com/bid/100925
- http://www.securitytracker.com/id/1039401
- https://access.redhat.com/errata/RHSA-2017:2789
- https://access.redhat.com/errata/RHSA-2017:2790
- https://access.redhat.com/errata/RHSA-2017:2791
- https://access.redhat.com/errata/RHSA-2017:2858
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbns03775en_us
- https://security.netapp.com/advisory/ntap-20170921-0001/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03817en_us
- https://www.debian.org/security/2017/dsa-3983
- https://www.synology.com/support/security/Synology_SA_17_57_Samba
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-12163
- https://www.samba.org/samba/security/CVE-2017-12163.html
