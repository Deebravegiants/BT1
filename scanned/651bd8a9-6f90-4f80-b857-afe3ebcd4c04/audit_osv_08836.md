# [H] CVE-2016-6301

## Summary
Severity: High
Advisory: CVE-2016-6301
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-6301
Type: osv

## Details
The recv_and_process_client_pkt function in networking/ntpd.c in busybox allows remote attackers to cause a denial of service (CPU and bandwidth consumption) via a forged NTP packet, which triggers a communication loop.

## References
- http://packetstormsecurity.com/files/153278/WAGO-852-Industrial-Managed-Switch-Series-Code-Execution-Hardcoded-Credentials.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://seclists.org/fulldisclosure/2020/Aug/20
- http://seclists.org/fulldisclosure/2020/Mar/15
- https://seclists.org/bugtraq/2019/Jun/14
- https://seclists.org/bugtraq/2019/Sep/7
- http://www.openwall.com/lists/oss-security/2016/08/03/7
- http://www.securityfocus.com/bid/92277
- https://security.gentoo.org/glsa/201701-05
- https://bugzilla.redhat.com/show_bug.cgi?id=1363710
- https://git.busybox.net/busybox/commit/?id=150dc7a2b483b8338a3e185c478b4b23ee884e71
