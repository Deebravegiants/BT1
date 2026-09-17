# [M] CVE-2016-2115

## Summary
Severity: Medium
Advisory: CVE-2016-2115
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-2115
Type: osv

## Details
Samba 3.x and 4.x before 4.2.11, 4.3.x before 4.3.8, and 4.4.x before 4.4.2 does not require SMB signing within a DCERPC session over ncacn_np, which allows man-in-the-middle attackers to spoof SMB clients by modifying the client-server data stream.

## References
- http://badlock.org/
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182185.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182272.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182288.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securitytracker.com/id/1035533
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.458012
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docId=emr_na-c05087821
- https://www.samba.org/samba/history/samba-4.2.10.html
- https://www.samba.org/samba/latest_news.html#4.4.2
- http://rhn.redhat.com/errata/RHSA-2016-0611.html
- http://rhn.redhat.com/errata/RHSA-2016-0612.html
