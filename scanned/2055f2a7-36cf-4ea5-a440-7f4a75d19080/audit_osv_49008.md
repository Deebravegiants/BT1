# [M] CVE-2018-20169

## Summary
Severity: Medium
Advisory: CVE-2018-20169
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-17
Source: https://osv.dev/vulnerability/CVE-2018-20169
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.19.9. The USB subsystem mishandles size checks during the reading of an extra descriptor, related to __usb_get_extra_descriptor in drivers/usb/core/usb.c.

## References
- https://usn.ubuntu.com/3879-2/
- https://usn.ubuntu.com/4094-1/
- https://access.redhat.com/errata/RHSA-2019:3517
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://lists.debian.org/debian-lts-announce/2019/05/msg00002.html
- https://usn.ubuntu.com/3879-1/
- https://usn.ubuntu.com/4118-1/
- https://access.redhat.com/errata/RHSA-2019:3309
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=704620afc70cf47abb9d6a1a57f3825d2bca49cf
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.9
- https://github.com/torvalds/linux/commit/704620afc70cf47abb9d6a1a57f3825d2bca49cf
