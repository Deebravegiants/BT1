# [M] CVE-2019-15921

## Summary
Severity: Medium
Advisory: CVE-2019-15921
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15921
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.6. There is a memory leak issue when idr_alloc() fails in genl_register_family() in net/netlink/genetlink.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.6
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://github.com/torvalds/linux/commit/ceabee6c59943bdd5e1da1a6a20dc7ee5f8113a2
