# [M] CVE-2019-15666

## Summary
Severity: Medium
Advisory: CVE-2019-15666
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-27
Source: https://osv.dev/vulnerability/CVE-2019-15666
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.19. There is an out-of-bounds array access in __xfrm_policy_unlink, which will cause denial of service, because verify_newpolicy_info in net/xfrm/xfrm_user.c mishandles directory validation.

## References
- https://support.f5.com/csp/article/K53420251?utm_source=f5support&amp%3Butm_medium=RSS
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.19
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b805d78d300bcf2c83d6df7da0c818b0fee41427
