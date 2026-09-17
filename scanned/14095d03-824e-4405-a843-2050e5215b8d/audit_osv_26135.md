# [H] CVE-2023-51779

## Summary
Severity: High
Advisory: CVE-2023-51779
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2023-51779
Type: osv

## Details
bt_sock_recvmsg in net/bluetooth/af_bluetooth.c in the Linux kernel through 6.6.8 has a use-after-free because of a bt_sock_ioctl race condition.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://github.com/torvalds/linux/commit/2e07e8348ea454615e268222ae3fc240421be768
