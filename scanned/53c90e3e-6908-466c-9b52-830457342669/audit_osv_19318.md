# [M] CVE-2021-20196

## Summary
Severity: Medium
Advisory: CVE-2021-20196
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-20196
Type: osv

## Details
A NULL pointer dereference flaw was found in the floppy disk emulator of QEMU. This issue occurs while processing read/write ioport commands if the selected floppy drive is not initialized with a block device. This flaw allows a privileged guest user to crash the QEMU process on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00002.html
- https://lists.debian.org/debian-lts-announce/2022/09/msg00008.html
- https://security.netapp.com/advisory/ntap-20210708-0004/
- https://bugs.launchpad.net/qemu/+bug/1912780
- https://www.openwall.com/lists/oss-security/2021/01/28/1
