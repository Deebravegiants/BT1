# [M] CVE-2019-19068

## Summary
Severity: Medium
Advisory: CVE-2019-19068
CVSS: 4.6 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19068
Type: osv

## Details
A memory leak in the rtl8xxxu_submit_int_urb() function in drivers/net/wireless/realtek/rtl8xxxu/rtl8xxxu_core.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering usb_submit_urb() failures, aka CID-a2cdd07488e6.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://usn.ubuntu.com/4300-1/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4286-2/
- https://usn.ubuntu.com/4301-1/
- https://usn.ubuntu.com/4302-1/
- https://github.com/torvalds/linux/commit/a2cdd07488e666aa93a49a3fc9c9b1299e27ef3c
