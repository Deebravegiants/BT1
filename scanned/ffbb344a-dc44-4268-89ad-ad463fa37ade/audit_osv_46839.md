# [M] CVE-2015-5299

## Summary
Severity: Medium
Advisory: CVE-2015-5299
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2015-12-29
Source: https://osv.dev/vulnerability/CVE-2015-5299
Type: osv

## Details
The shadow_copy2_get_shadow_copy_data function in modules/vfs_shadow_copy2.c in Samba 3.x and 4.x before 4.1.22, 4.2.x before 4.2.7, and 4.3.x before 4.3.3 does not verify that the DIRECTORY_LIST access right has been granted, which allows remote attackers to access snapshots by visiting a shadow copy directory.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/174076.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-December/174391.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2015-12/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-01/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://www.debian.org/security/2016/dsa-3433
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjan2016-2867209.html
- http://www.securityfocus.com/bid/79729
- http://www.securitytracker.com/id/1034493
- http://www.ubuntu.com/usn/USN-2855-1
- http://www.ubuntu.com/usn/USN-2855-2
- https://bugzilla.redhat.com/show_bug.cgi?id=1276126
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05115993
