# [M] CVE-2019-15807

## Summary
Severity: Medium
Advisory: CVE-2019-15807
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/CVE-2019-15807
Type: osv

## Details
In the Linux kernel before 5.1.13, there is a memory leak in drivers/scsi/libsas/sas_expander.c when SAS expander discovery fails. This will cause a BUG and denial of service.

## References
- https://support.f5.com/csp/article/K52136304?utm_source=f5support&amp%3Butm_medium=RSS
- https://lists.debian.org/debian-lts-announce/2019/09/msg00014.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00015.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.13
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=3b0541791453fbe7f42867e310e0c9eb6295364d
