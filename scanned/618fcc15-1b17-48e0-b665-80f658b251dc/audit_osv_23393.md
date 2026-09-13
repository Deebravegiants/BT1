# [M] cgroup: Add missing cpus_read_lock() to cgroup_attach_task_all()

## Summary
Severity: Medium
Advisory: CVE-2022-48671
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2022-48671
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.213 <5.4.215, >=5.10.143 <5.10.145, >=5.15.68 <5.15.70, >=5.19.9 <5.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

cgroup: Add missing cpus_read_lock() to cgroup_attach_task_all()

syzbot is hitting percpu_rwsem_assert_held(&cpu_hotplug_lock) warning at
cpuset_attach() [1], for commit 4f7e7236435ca0ab ("cgroup: Fix
threadgroup_rwsem <-> cpus_read_lock() deadlock") missed that
cpuset_attach() is also called from cgroup_attach_task_all().
Add cpus_read_lock() like what cgroup_procs_write_start() does.

## References
- https://git.kernel.org/stable/c/07191f984842d50020789ff14c75da436a7f46a9
- https://git.kernel.org/stable/c/321488cfac7d0eb6d97de467015ff754f85813ff
- https://git.kernel.org/stable/c/43626dade36fa74d3329046f4ae2d7fdefe401c6
- https://git.kernel.org/stable/c/5db17805b6ba4c34dab303f49aea3562fc25af75
- https://git.kernel.org/stable/c/99bc25748e394d17f9e8b10cc7f273b8e64c1c7e
- https://git.kernel.org/stable/c/9f267393b036f1470fb12fb892d59e7ff8aeb58d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48671.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
