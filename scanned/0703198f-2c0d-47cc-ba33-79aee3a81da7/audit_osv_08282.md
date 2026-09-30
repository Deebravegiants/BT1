# [M] CVE-2016-2114

## Summary
Severity: Medium
Advisory: CVE-2016-2114
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-2114
Type: osv

## Details
The SMB1 protocol implementation in Samba 4.x before 4.2.11, 4.3.x before 4.3.8, and 4.4.x before 4.4.2 does not recognize the "server signing = mandatory" setting, which allows man-in-the-middle attackers to spoof SMB servers by modifying the client-server data stream.

## References
- http://badlock.org/
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182185.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182272.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182288.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/86011
- http://www.securitytracker.com/id/1035533
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.458012
- https://www.samba.org/samba/history/samba-4.2.10.html
- https://www.samba.org/samba/latest_news.html#4.4.2
- http://rhn.redhat.com/errata/RHSA-2016-0612.html
- http://rhn.redhat.com/errata/RHSA-2016-0614.html
- http://rhn.redhat.com/errata/RHSA-2016-0618.html
- http://rhn.redhat.com/errata/RHSA-2016-0620.html
- http://www.debian.org/security/2016/dsa-3548
- http://www.ubuntu.com/usn/USN-2950-1
- http://www.ubuntu.com/usn/USN-2950-2
- http://www.ubuntu.com/usn/USN-2950-3
