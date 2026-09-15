# [M] CVE-2024-0443

## Summary
Severity: Medium
Advisory: CVE-2024-0443
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-12
Source: https://osv.dev/vulnerability/CVE-2024-0443
Type: osv

## Details
A flaw was found in the blkgs destruction path in block/blk-cgroup.c in the Linux kernel, leading to a cgroup blkio memory leakage problem. When a cgroup is being destroyed, cgroup_rstat_flush() is only called at css_release_work_fn(), which is called when the blkcg reference count reaches 0. This circular dependency will prevent blkcg and some blkgs from being freed after they are made offline. This issue may allow an attacker with a local access to cause system instability, such as an out of memory error.

## References
- https://access.redhat.com/errata/RHSA-2023:7370
- https://access.redhat.com/security/cve/CVE-2024-0443
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/errata/RHSA-2023:7077
- https://bugzilla.redhat.com/show_bug.cgi?id=2257968
- https://lore.kernel.org/linux-block/20221215033132.230023-3-longman@redhat.com/
