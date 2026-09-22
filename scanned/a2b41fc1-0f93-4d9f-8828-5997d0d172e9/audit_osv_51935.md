# [M] CVE-2021-45868

## Summary
Severity: Medium
Advisory: CVE-2021-45868
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-03-18
Source: https://osv.dev/vulnerability/CVE-2021-45868
Type: osv

## Details
In the Linux kernel before 5.15.3, fs/quota/quota_tree.c does not validate the block number in the quota tree (on disk). This can, for example, lead to a kernel/locking/rwsem.c use-after-free if there is a corrupted quota file.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.3
- https://security.netapp.com/advisory/ntap-20220419-0003/
- https://bugzilla.kernel.org/show_bug.cgi?id=214655
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9bf3d20331295b1ecb81f4ed9ef358c51699a050
- https://www.openwall.com/lists/oss-security/2022/03/17/1
- https://www.openwall.com/lists/oss-security/2022/03/17/2
