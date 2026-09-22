# [M] CVE-2015-9261

## Summary
Severity: Medium
Advisory: CVE-2015-9261
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2015-9261
Type: osv

## Details
huft_build in archival/libarchive/decompress_gunzip.c in BusyBox before 1.27.2 misuses a pointer, causing segfaults and an application crash during an unzip operation on a specially crafted ZIP file.

## References
- http://packetstormsecurity.com/files/153278/WAGO-852-Industrial-Managed-Switch-Series-Code-Execution-Hardcoded-Credentials.html
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://packetstormsecurity.com/files/167552/Nexans-FTTO-GigaSwitch-Outdated-Components-Hardcoded-Backdoor.html
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://seclists.org/fulldisclosure/2020/Aug/20
- http://seclists.org/fulldisclosure/2022/Jun/36
- http://www.openwall.com/lists/oss-security/2015/10/25/3
- https://bugs.debian.org/803097
- https://git.busybox.net/busybox/commit/?id=1de25a6e87e0e627aa34298105a3d17c60a1f44e
- https://lists.debian.org/debian-lts-announce/2018/07/msg00037.html
- https://lists.debian.org/debian-lts-announce/2021/02/msg00020.html
- https://seclists.org/bugtraq/2019/Jun/14
- https://seclists.org/bugtraq/2019/Sep/7
- https://usn.ubuntu.com/3935-1/
- http://seclists.org/fulldisclosure/2019/Jun/18
- http://seclists.org/fulldisclosure/2019/Sep/7
- http://seclists.org/fulldisclosure/2020/Aug/20
- http://seclists.org/fulldisclosure/2022/Jun/36
- http://www.openwall.com/lists/oss-security/2015/10/25/3
