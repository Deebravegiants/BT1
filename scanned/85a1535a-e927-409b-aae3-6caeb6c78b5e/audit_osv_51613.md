# [M] CVE-2021-3564

## Summary
Severity: Medium
Advisory: CVE-2021-3564
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-3564
Type: osv

## Details
A flaw double-free memory corruption in the Linux kernel HCI device initialization subsystem was found in the way user attach malicious HCI TTY Bluetooth device. A local user could use this flaw to crash the system. This flaw affects all the Linux kernel versions starting from 3.13.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1964139
- https://www.openwall.com/lists/oss-security/2021/05/25/1
- http://www.openwall.com/lists/oss-security/2021/05/25/1
- http://www.openwall.com/lists/oss-security/2021/06/01/2
