# [M] CVE-2016-3115

## Summary
Severity: Medium
Advisory: CVE-2016-3115
CVSS: 6.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N)
Published: 2016-03-22
Source: https://osv.dev/vulnerability/CVE-2016-3115
Type: osv

## Details
Multiple CRLF injection vulnerabilities in session.c in sshd in OpenSSH before 7.2p2 allow remote authenticated users to bypass intended shell-command restrictions via crafted X11 forwarding data, related to the (1) do_authenticated1 and (2) session_x11_req functions.

## References
- http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/session.c
- http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/session.c.diff?r1=1.281&r2=1.282&f=h
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183101.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/183122.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/178838.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/179924.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-March/180491.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184264.html
- http://packetstormsecurity.com/files/136234/OpenSSH-7.2p1-xauth-Command-Injection-Bypass.html
- http://seclists.org/fulldisclosure/2016/Mar/46
- http://seclists.org/fulldisclosure/2016/Mar/47
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/84314
- http://www.securitytracker.com/id/1035249
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2016-3115
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://www.exploit-db.com/exploits/39569/
- http://rhn.redhat.com/errata/RHSA-2016-0465.html
- http://rhn.redhat.com/errata/RHSA-2016-0466.html
