# [M] CVE-2022-36879

## Summary
Severity: Medium
Advisory: CVE-2022-36879
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-07-27
Source: https://osv.dev/vulnerability/CVE-2022-36879
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.18.14. xfrm_expand_policies in net/xfrm/xfrm_policy.c can cause a refcount to be dropped twice.

## References
- https://www.debian.org/security/2022/dsa-5207
- https://lists.debian.org/debian-lts-announce/2022/09/msg00011.html
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://security.netapp.com/advisory/ntap-20220901-0007/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=f85daf0e725358be78dfd208dea5fd665d8cb901
- https://github.com/torvalds/linux/commit/f85daf0e725358be78dfd208dea5fd665d8cb901
