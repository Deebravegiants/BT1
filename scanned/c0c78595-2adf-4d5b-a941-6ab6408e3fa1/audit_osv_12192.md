# [H] CVE-2018-10858

## Summary
Severity: High
Advisory: CVE-2018-10858
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-10858
Type: osv

## Details
A heap-buffer overflow was found in the way samba clients processed extra long filename in a directory listing. A malicious samba server could use this flaw to cause arbitrary code execution on a samba client. Samba versions before 4.6.16, 4.7.9 and 4.8.4 are vulnerable.

## References
- https://kc.mcafee.com/corporate/index?page=content&id=SB10284
- http://www.securityfocus.com/bid/105085
- http://www.securitytracker.com/id/1042002
- https://access.redhat.com/errata/RHSA-2018:2612
- https://access.redhat.com/errata/RHSA-2018:2613
- https://access.redhat.com/errata/RHSA-2018:3056
- https://access.redhat.com/errata/RHSA-2018:3470
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20180814-0001/
- https://usn.ubuntu.com/3738-1/
- https://www.debian.org/security/2018/dsa-4271
- https://www.samba.org/samba/security/CVE-2018-10858.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10858
