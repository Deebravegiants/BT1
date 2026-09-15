# [M] CVE-2015-7560

## Summary
Severity: Medium
Advisory: CVE-2015-7560
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-03-13
Source: https://osv.dev/vulnerability/CVE-2015-7560
Type: osv

## Details
The SMB1 implementation in smbd in Samba 3.x and 4.x before 4.1.23, 4.2.x before 4.2.9, 4.3.x before 4.3.6, and 4.4.x before 4.4.0rc4 allows remote authenticated users to modify arbitrary ACLs by using a UNIX SMB1 call to create a symlink, and then using a non-UNIX SMB1 call to write to the ACL content.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178730.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178764.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/180000.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00065.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00081.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00090.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00092.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://www.debian.org/security/2016/dsa-3514
- http://www.securityfocus.com/bid/84267
- http://www.securitytracker.com/id/1035220
- http://www.ubuntu.com/usn/USN-2922-1
- https://bugzilla.samba.org/show_bug.cgi?id=11648
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05121842
- https://www.samba.org/samba/security/CVE-2015-7560.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178730.html
