# [H] CVE-2021-42252

## Summary
Severity: High
Advisory: CVE-2021-42252
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-42252
Type: osv

## Details
An issue was discovered in aspeed_lpc_ctrl_mmap in drivers/soc/aspeed/aspeed-lpc-ctrl.c in the Linux kernel before 5.14.6. Local attackers able to access the Aspeed LPC control interface could overwrite memory in the kernel and potentially execute privileges, aka CID-b49a0e69a7b1. This occurs because a certain comparison uses values that are not memory sizes.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.6
- https://security.netapp.com/advisory/ntap-20211112-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b49a0e69a7b1a68c8d3f64097d06dabb770fec96
