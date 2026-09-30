# [C] CVE-2019-15504

## Summary
Severity: Critical
Advisory: CVE-2019-15504
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-23
Source: https://osv.dev/vulnerability/CVE-2019-15504
Type: osv

## Details
drivers/net/wireless/rsi/rsi_91x_usb.c in the Linux kernel through 5.2.9 has a Double Free via crafted USB device traffic (which may be remote via usbip or usbredir).

## References
- https://support.f5.com/csp/article/K33554143?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3RUDQJXRJQVGHCGR4YZWTQ3ECBI7TXH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T4JZ6AEUKFWBHQAROGMQARJ274PQP2QP/
- https://lore.kernel.org/lkml/20190819220230.10597-1-benquike%40gmail.com/
- https://security.netapp.com/advisory/ntap-20190905-0002/
- https://support.f5.com/csp/article/K33554143
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4157-2/
