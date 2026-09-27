# [C] CVE-2021-31535

## Summary
Severity: Critical
Advisory: CVE-2021-31535
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2021-31535
Type: osv

## Details
LookupCol.c in X.Org X through X11R7.7 and libX11 before 1.7.1 might allow remote attackers to execute arbitrary code. The libX11 XLookupColor request (intended for server-side color lookup) contains a flaw allowing a client to send color-name requests with a name longer than the maximum size allowed by the protocol (and also longer than the maximum packet size for normal-sized packets). The user-controlled data exceeding the maximum size is then interpreted by the server as additional X protocol requests and executed, e.g., to disable X server authorization completely. For example, if the victim encounters malicious terminal control sequences for color codes, then the attacker may be able to take full control of the running graphical session.

## References
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r61db8e7dcb56dc000a5387a88f7a473bacec5ee01b9ff3f55308aacc%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cusers.kafka.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TEOT4RLB76RVPJQKGGTIKTBIOLHX2NR6/
- http://seclists.org/fulldisclosure/2021/May/52
- http://www.openwall.com/lists/oss-security/2021/05/18/2
- https://gitlab.freedesktop.org/xorg/lib/libx11/-/commit/8d2e02ae650f00c4a53deb625211a0527126c605
- https://lists.debian.org/debian-lts-announce/2021/05/msg00021.html
- https://lists.freedesktop.org/archives/xorg/
- https://lists.x.org/archives/xorg-announce/2021-May/003088.html
- https://security.gentoo.org/glsa/202105-16
- https://security.netapp.com/advisory/ntap-20210813-0001/
- https://www.debian.org/security/2021/dsa-4920
- https://www.openwall.com/lists/oss-security/2021/05/18/2
- https://www.openwall.com/lists/oss-security/2021/05/18/3
- http://packetstormsecurity.com/files/162737/libX11-Insufficient-Length-Check-Injection.html
- https://unparalleled.eu/blog/2021/20210518-using-xterm-to-navigate-the-huge-color-space/
- https://unparalleled.eu/publications/2021/advisory-unpar-2021-1.txt
