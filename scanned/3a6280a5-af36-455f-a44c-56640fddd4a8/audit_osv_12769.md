# [M] CVE-2018-14665

## Summary
Severity: Medium
Advisory: CVE-2018-14665
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-25
Source: https://osv.dev/vulnerability/CVE-2018-14665
Type: osv

## Details
A flaw was found in xorg-x11-server before 1.20.3. An incorrect permission check for -modulepath and -logfile options when starting Xorg. X server allows unprivileged users with the ability to log in to the system via physical console to escalate their privileges and run arbitrary code under root privileges.

## References
- http://packetstormsecurity.com/files/154942/Xorg-X11-Server-SUID-modulepath-Privilege-Escalation.html
- http://packetstormsecurity.com/files/155276/Xorg-X11-Server-Local-Privilege-Escalation.html
- http://www.securityfocus.com/bid/105741
- http://www.securitytracker.com/id/1041948
- https://access.redhat.com/errata/RHSA-2018:3410
- https://security.gentoo.org/glsa/201810-09
- https://usn.ubuntu.com/3802-1/
- https://www.debian.org/security/2018/dsa-4328
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14665
- https://gitlab.freedesktop.org/xorg/xserver/commit/50c0cf885a6e91c0ea71fb49fa8f1b7c86fe330e
- https://gitlab.freedesktop.org/xorg/xserver/commit/8a59e3b7dbb30532a7c3769c555e00d7c4301170
- https://lists.x.org/archives/xorg-announce/2018-October/002927.html
- https://www.exploit-db.com/exploits/45697/
- https://www.exploit-db.com/exploits/45742/
- https://www.exploit-db.com/exploits/45832/
- https://www.exploit-db.com/exploits/45908/
- https://www.exploit-db.com/exploits/45922/
- https://www.exploit-db.com/exploits/45938/
- https://www.exploit-db.com/exploits/46142/
- https://www.securepatterns.com/2018/10/cve-2018-14665-xorg-x-server.html
