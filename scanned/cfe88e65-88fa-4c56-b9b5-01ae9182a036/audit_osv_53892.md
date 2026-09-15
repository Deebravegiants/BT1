# [M] CVE-2023-31083

## Summary
Severity: Medium
Advisory: CVE-2023-31083
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-31083
Type: osv

## Details
An issue was discovered in drivers/bluetooth/hci_ldisc.c in the Linux kernel 6.2. In hci_uart_tty_ioctl, there is a race condition between HCIUARTSETPROTO and HCIUARTGETPROTO. HCI_UART_PROTO_SET is set before hu->proto is set. A NULL pointer dereference may occur.

## References
- https://lore.kernel.org/all/CA+UBctC3p49aTgzbVgkSZ2+TQcqq4fPDO7yZitFT5uBPDeCO2g%40mail.gmail.com/
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9c33663af9ad115f90c076a1828129a3fbadea98
- https://security.netapp.com/advisory/ntap-20230929-0003/
- https://bugzilla.suse.com/show_bug.cgi?id=1210780
