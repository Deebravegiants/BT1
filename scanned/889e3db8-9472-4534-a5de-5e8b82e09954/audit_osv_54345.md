# [M] CVE-2023-50431

## Summary
Severity: Medium
Advisory: CVE-2023-50431
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-09
Source: https://osv.dev/vulnerability/CVE-2023-50431
Type: osv

## Details
sec_attest_info in drivers/accel/habanalabs/common/habanalabs_ioctl.c in the Linux kernel through 6.6.5 allows an information leak to user space because info->pad0 is not initialized.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=a9f07790a4b2250f0140e9a61c7f842fd9b618c7
- https://lists.freedesktop.org/archives/dri-devel/2023-November/431772.html
