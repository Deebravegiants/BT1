# [H] CVE-2020-36385

## Summary
Severity: High
Advisory: CVE-2020-36385
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-07
Source: https://osv.dev/vulnerability/CVE-2020-36385
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.10. drivers/infiniband/core/ucma.c has a use-after-free because the ctx is reached via the ctx_list in some ucma_migrate_id situations where ucma_close is called, aka CID-f5449e74802c.

## References
- https://www.starwindsoftware.com/security/sw-20220802-0002/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10
- https://security.netapp.com/advisory/ntap-20210720-0004/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f5449e74802c1112dea984aec8af7a33c4516af1
- https://sites.google.com/view/syzscope/kasan-use-after-free-read-in-ucma_close-2
- https://syzkaller.appspot.com/bug?id=457491c4672d7b52c1007db213d93e47c711fae6
