# [H] CVE-2019-16714

## Summary
Severity: High
Advisory: CVE-2019-16714
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-09-23
Source: https://osv.dev/vulnerability/CVE-2019-16714
Type: osv

## Details
In the Linux kernel before 5.2.14, rds6_inc_info_copy in net/rds/recv.c allows attackers to obtain sensitive information from kernel stack memory because tos and flags fields are not initialized.

## References
- https://support.f5.com/csp/article/K48351130?utm_source=f5support&amp%3Butm_medium=RSS
- https://security.netapp.com/advisory/ntap-20191031-0005/
- https://usn.ubuntu.com/4157-1/
- https://usn.ubuntu.com/4157-2/
- http://www.openwall.com/lists/oss-security/2019/09/24/2
- http://www.openwall.com/lists/oss-security/2019/09/25/1
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.14
- https://github.com/torvalds/linux/commit/7d0a06586b2686ba80c4a2da5f91cb10ffbea736
