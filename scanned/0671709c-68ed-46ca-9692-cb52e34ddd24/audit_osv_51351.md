# [M] CVE-2021-29265

## Summary
Severity: Medium
Advisory: CVE-2021-29265
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-26
Source: https://osv.dev/vulnerability/CVE-2021-29265
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.11.7. usbip_sockfd_store in drivers/usb/usbip/stub_dev.c allows attackers to cause a denial of service (GPF) because the stub-up sequence has race conditions during an update of the local and shared status, aka CID-9380afd6df70.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.7
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=9380afd6df70e24eacbdbde33afc6a3950965d22
