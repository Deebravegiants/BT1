# [M] CVE-2020-36691

## Summary
Severity: Medium
Advisory: CVE-2020-36691
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2020-36691
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.8. lib/nlattr.c allows attackers to cause a denial of service (unbounded recursion) via a nested Netlink policy with a back reference.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8
- https://github.com/torvalds/linux/commit/7690aa1cdf7c4565ad6b013b324c28b685505e24
