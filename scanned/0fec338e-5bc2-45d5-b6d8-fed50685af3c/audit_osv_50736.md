# [M] CVE-2020-36557

## Summary
Severity: Medium
Advisory: CVE-2020-36557
CVSS: 5.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-21
Source: https://osv.dev/vulnerability/CVE-2020-36557
Type: osv

## Details
A race condition in the Linux kernel before 5.6.2 between the VT_DISALLOCATE ioctl and closing/opening of ttys could lead to a use-after-free.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.2
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=ca4463bf8438b403596edd0ec961ca0d4fbe0220
