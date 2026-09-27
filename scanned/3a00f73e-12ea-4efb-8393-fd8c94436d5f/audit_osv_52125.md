# [H] CVE-2021-47101

## Summary
Severity: High
Advisory: CVE-2021-47101
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47101
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

asix: fix uninit-value in asix_mdio_read()

asix_read_cmd() may read less than sizeof(smsr) bytes and in this case
smsr will be uninitialized.

Fail log:
BUG: KMSAN: uninit-value in asix_check_host_enable drivers/net/usb/asix_common.c:82 [inline]
BUG: KMSAN: uninit-value in asix_check_host_enable drivers/net/usb/asix_common.c:82 [inline] drivers/net/usb/asix_common.c:497
BUG: KMSAN: uninit-value in asix_mdio_read+0x3c1/0xb00 drivers/net/usb/asix_common.c:497 drivers/net/usb/asix_common.c:497
 asix_check_host_enable drivers/net/usb/asix_common.c:82 [inline]
 asix_check_host_enable drivers/net/usb/asix_common.c:82 [inline] drivers/net/usb/asix_common.c:497
 asix_mdio_read+0x3c1/0xb00 drivers/net/usb/asix_common.c:497 drivers/net/usb/asix_common.c:497

## References
- https://git.kernel.org/stable/c/8035b1a2a37a29d8c717ef84fca8fe7278bc9f03
- https://git.kernel.org/stable/c/d259f621c85949f30cc578cac813b82bb5169f56
