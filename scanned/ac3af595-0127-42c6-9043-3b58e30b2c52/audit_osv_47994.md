# [M] CVE-2017-16538

## Summary
Severity: Medium
Advisory: CVE-2017-16538
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-04
Source: https://osv.dev/vulnerability/CVE-2017-16538
Type: osv

## Details
drivers/media/usb/dvb-usb-v2/lmedm04.c in the Linux kernel through 4.13.11 allows local users to cause a denial of service (general protection fault and system crash) or possibly have unspecified other impact via a crafted USB device, related to a missing warm-start check and incorrect attach timing (dm04_lme2510_frontend_attach versus dm04_lme2510_tuner).

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- https://usn.ubuntu.com/3631-1/
- https://usn.ubuntu.com/3631-2/
- https://usn.ubuntu.com/3754-1/
- https://www.debian.org/security/2018/dsa-4082
- https://www.debian.org/security/2017/dsa-4073
- https://groups.google.com/d/msg/syzkaller/XwNidsl4X04/ti6I2IaRBAAJ
- https://patchwork.linuxtv.org/patch/44567/
- https://patchwork.linuxtv.org/patch/44566/
