# [M] CVE-2019-15924

## Summary
Severity: Medium
Advisory: CVE-2019-15924
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15924
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.11. fm10k_init_module in drivers/net/ethernet/intel/fm10k/fm10k_main.c has a NULL pointer dereference because there is no -ENOMEM upon an alloc_workqueue failure.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.11
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://github.com/torvalds/linux/commit/01ca667133d019edc9f0a1f70a272447c84ec41f
