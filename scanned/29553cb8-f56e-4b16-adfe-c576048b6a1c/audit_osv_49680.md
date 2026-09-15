# [H] CVE-2019-15916

## Summary
Severity: High
Advisory: CVE-2019-15916
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2019-15916
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.0.1. There is a memory leak in register_queue_kobjects() in net/core/net-sysfs.c, which will cause denial of service.

## References
- https://support.f5.com/csp/article/K57418558?utm_source=f5support&amp%3Butm_medium=RSS
- https://security.netapp.com/advisory/ntap-20191004-0001/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://access.redhat.com/errata/RHSA-2019:3309
- https://access.redhat.com/errata/RHSA-2019:3517
- https://access.redhat.com/errata/RHSA-2020:0740
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=895a5e96dbd6386c8e78e5b78e067dcc67b7f0ab
