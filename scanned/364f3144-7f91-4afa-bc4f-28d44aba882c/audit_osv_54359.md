# [H] CVE-2023-51780

## Summary
Severity: High
Advisory: CVE-2023-51780
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-11
Source: https://osv.dev/vulnerability/CVE-2023-51780
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.6.8. do_vcc_ioctl in net/atm/ioctl.c has a use-after-free because of a vcc_recvmsg race condition.

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://security.netapp.com/advisory/ntap-20240419-0001/
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.8
- https://lists.debian.org/debian-lts-announce/2024/01/msg00004.html
- https://github.com/torvalds/linux/commit/24e90b9e34f9e039f56b5f25f6e6eb92cdd8f4b3
