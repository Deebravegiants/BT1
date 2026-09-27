# [M] CVE-2016-2110

## Summary
Severity: Medium
Advisory: CVE-2016-2110
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-04-25
Source: https://osv.dev/vulnerability/CVE-2016-2110
Type: osv

## Details
The NTLMSSP authentication implementation in Samba 3.x and 4.x before 4.2.11, 4.3.x before 4.3.8, and 4.4.x before 4.4.2 allows man-in-the-middle attackers to perform protocol-downgrade attacks by modifying the client-server data stream to remove application-layer flags or encryption settings, as demonstrated by clearing the NTLMSSP_NEGOTIATE_SEAL or NTLMSSP_NEGOTIATE_SIGN option to disrupt LDAP security.

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
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00046.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00124.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securitytracker.com/id/1035533
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.458012
- https://h20566.www2.hpe.com/hpsc/doc/public/display?docId=emr_na-c05087821
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05082964
- https://h20566.www2.hpe.com/portal/site/hpsc/public/kb/docDisplay?docId=emr_na-c05162399
