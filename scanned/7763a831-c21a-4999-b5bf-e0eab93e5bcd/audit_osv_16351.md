# [H] CVE-2019-5747

## Summary
Severity: High
Advisory: CVE-2019-5747
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-01-09
Source: https://osv.dev/vulnerability/CVE-2019-5747
Type: osv

## Details
An issue was discovered in BusyBox through 1.30.0. An out of bounds read in udhcp components (consumed by the DHCP client, server, and/or relay) might allow a remote attacker to leak sensitive information from the stack by sending a crafted DHCP message. This is related to assurance of a 4-byte length when decoding DHCP_SUBNET. NOTE: this issue exists because of an incomplete fix for CVE-2018-20679.

## References
- http://seclists.org/fulldisclosure/2019/Sep/7
- https://seclists.org/bugtraq/2019/Sep/7
- https://usn.ubuntu.com/3935-1/
- https://bugs.busybox.net/show_bug.cgi?id=11506
- https://git.busybox.net/busybox/commit/?id=74d9f1ba37010face4bd1449df4d60dd84450b06
- http://packetstormsecurity.com/files/154361/Cisco-Device-Hardcoded-Credentials-GNU-glibc-BusyBox.html
