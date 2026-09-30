# [H] bpf,fork: wipe ->bpf_storage before bailouts that access it

## Summary
Severity: High
Advisory: CVE-2026-72110
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72110
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf,fork: wipe ->bpf_storage before bailouts that access it

Currently, copy_process() can bail out to free_task() before p->bpf_storage
has been initialized, with this call graph (shown here for the
!CONFIG_MEMCG case):

copy_process
  dup_task_struct
    arch_dup_task_struct
      [copies the entire task_struct, including ->bpf_storage member]
  [RLIMIT_NPROC check fails]
  delayed_free_task
    free_task
      bpf_task_storage_free
        rcu_dereference(task->bpf_storage)
        bpf_local_storage_destroy

In this case, the nascent task's ->bpf_storage member that
bpf_local_storage_destroy() operates on is a plain copy of the parent's
->bpf_storage pointer, not a real initialized pointer.
This leads to badness (kernel hangs, UAF).

This is reachable as long as the process calling fork() has been inserted
into a task storage map.

## References
- https://git.kernel.org/stable/c/43f0005f81b8ce3be962d653cde8db9022f1e9b0
- https://git.kernel.org/stable/c/7df67a4799067a59e6a2d53f8059a6be6e73e678
- https://git.kernel.org/stable/c/9b51a6155d14389876916726430da30eabb1d4ed
- https://git.kernel.org/stable/c/9cff220ddb65b022cc668bb652200742476e744c
- https://git.kernel.org/stable/c/aff686efd38728e06daf12417a0d7ed454ce4cff
- https://git.kernel.org/stable/c/c3fd6f28c7ce1142a3b23dbb840eaa4777de1d74
- https://git.kernel.org/stable/c/c4f626ddf2350652ad2f79daf1f10847f3f6eabd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72110.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72110
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
