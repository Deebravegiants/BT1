# [M] CVE-2023-2002

## Summary
Severity: Medium
Advisory: CVE-2023-2002
CVSS: 6.8 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-2002
Type: osv

## Details
A vulnerability was found in the HCI sockets implementation due to a missing capability check in net/bluetooth/hci_sock.c in the Linux Kernel. This flaw allows an attacker to unauthorized execution of management commands, compromising the confidentiality, integrity, and availability of Bluetooth communication.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20240202-0004/
- https://www.debian.org/security/2023/dsa-5480
- https://lists.debian.org/debian-lts-announce/2023/07/msg00030.html
- https://www.openwall.com/lists/oss-security/2023/04/16/3
