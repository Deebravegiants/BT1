# [H] CVE-2016-2147

## Summary
Severity: High
Advisory: CVE-2016-2147
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-2147
Type: osv

## Details
Integer overflow in the DHCP client (udhcpc) in BusyBox before 1.25.0 allows remote attackers to cause a denial of service (crash) via a malformed RFC1035-encoded domain name, which triggers an out-of-bounds heap write.

## References
- https://busybox.net/news.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00037.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00020.html
- https://security.gentoo.org/glsa/201612-04
- https://usn.ubuntu.com/3935-1/
- http://www.openwall.com/lists/oss-security/2016/03/11/16
- https://git.busybox.net/busybox/commit/?id=d474ffc68290e0a83651c4432eeabfa62cd51e87
- http://packetstormsecurity.com/files/153278/WAGO-852-Industrial-Managed-Switch-Series-Code-Execution-Hardcoded-Credentials.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://seclists.org/fulldisclosure/2020/Aug/20
- https://seclists.org/bugtraq/2019/Jun/14
- https://seclists.org/bugtraq/2019/Sep/7
