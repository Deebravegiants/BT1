# [M] CVE-2023-28328

## Summary
Severity: Medium
Advisory: CVE-2023-28328
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-28328
Type: osv

## Details
A NULL pointer dereference flaw was found in the az6027 driver in drivers/media/usb/dev-usb/az6027.c in the Linux Kernel. The message from user space is not checked properly before transferring into the device. This flaw allows a local user to crash the system or potentially cause a denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2177389
