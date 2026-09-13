# [H] CVE-2018-20679

## Summary
Severity: High
Advisory: CVE-2018-20679
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/CVE-2018-20679
Type: osv

## Details
An issue was discovered in BusyBox before 1.30.0. An out of bounds read in udhcp components (consumed by the DHCP server, client, and relay) allows a remote attacker to leak sensitive information from the stack by sending a crafted DHCP message. This is related to verification in udhcp_get_option() in networking/udhcp/common.c that 4-byte options are indeed 4 bytes.

## References
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
- http://seclists.org/fulldisclosure/2019/Sep/7
- https://seclists.org/bugtraq/2019/Sep/7
- https://busybox.net/news.html
- https://usn.ubuntu.com/3935-1/
- https://bugs.busybox.net/show_bug.cgi?id=11506
- https://git.busybox.net/busybox/commit/?id=6d3b4bb24da9a07c263f3c1acf8df85382ff562c
