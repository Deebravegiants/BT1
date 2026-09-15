# [H] bpf: use kvfree() for replaced sysctl write buffer

## Summary
Severity: High
Advisory: CVE-2026-63809
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63809
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.260, >=5.11.0 <5.15.211, >=5.12.0 <6.1.177, >=5.16.0 <6.6.144, >=6.2.0 <6.12.95, >=6.7.0 <6.18.38, >=6.13.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: use kvfree() for replaced sysctl write buffer

proc_sys_call_handler() allocates its temporary sysctl buffer with
kvzalloc() and passes it to __cgroup_bpf_run_filter_sysctl(). Since
kvzalloc() may fall back to vmalloc() for large allocations, freeing
that buffer with kfree() is wrong and can corrupt memory.

Use kvfree() to safely handle both kmalloc and kvzalloc()/vmalloc
allocations.

The bug was first flagged by an experimental analysis tool we are
developing for kernel memory-management bugs while analyzing
v6.13-rc1. The tool is still under development and is not yet publicly
available. Manual inspection confirms that the bug is still
present in v7.1-rc5.

Reproduced the bug based on v7.1-rc4 in a QEMU x86_64 guest booted with
KASAN and CONFIG_FAILSLAB enabled. To exercise the replacement path, the
test tree also included the accompanying fix for the stale ret == 1
check in __cgroup_bpf_run_filter_sysctl(). The reproducer confines
failslab injections to the proc_sys_call_handler() range, uses
stacktrace-depth=32, and injects fail-nth=1 while writing 8191 bytes to
/proc/sys/kernel/domainname from a task in the target cgroup. Under
that setup, fail-nth=1 triggered the fault:

  BUG: unable to handle page fault for address: ffffeb0200024d48
  #PF: supervisor read access in kernel mode
  #PF: error_code(0x0000) - not-present page
  PGD 0 P4D 0
  Oops: Oops: 0000  SMP KASAN NOPTI
  CPU: 2 UID: 0 PID: 209 Comm: repro_proc_sys_ Not tainted 7.1.0-rc4-00686-g97625979a5d4  PREEMPT(lazy)
  Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.15.0-1 04/01/2014
  RIP: 0010:kfree+0x6e/0x510
  ...
  Call Trace:
   <TASK>
   ? __cgroup_bpf_run_filter_sysctl+0x626/0xc30
   __cgroup_bpf_run_filter_sysctl+0x74d/0xc30
   ? __pfx___cgroup_bpf_run_filter_sysctl+0x10/0x10
   ? srso_return_thunk+0x5/0x5f
   ? __kvmalloc_node_noprof+0x345/0x870
   ? proc_sys_call_handler+0x250/0x480
   ? srso_return_thunk+0x5/0x5f
   proc_sys_call_handler+0x3a2/0x480
   ? __pfx_proc_sys_call_handler+0x10/0x10
   ? srso_return_thunk+0x5/0x5f
   ? selinux_file_permission+0x39f/0x500
   ? srso_return_thunk+0x5/0x5f
   ? lock_is_held_type+0x9e/0x120
   vfs_write+0x98e/0x1000
   ...
   </TASK>

With this fix applied on top of the same test setup, rerunning the
reproducer with fail-nth=1 yields no corresponding Oops reports.

## References
- https://git.kernel.org/stable/c/4c21b5927d4364bfe7365f2700da5fea0ed0d004
- https://git.kernel.org/stable/c/65bd0c0afb0e1bf3287458e342429b069624f7d4
- https://git.kernel.org/stable/c/70df4de46577fab5e25418f014583155a147c902
- https://git.kernel.org/stable/c/77355ef7a9f6b0d2bdf65be3b37f2c1f365e20d2
- https://git.kernel.org/stable/c/81fc9a13acae99966232f0e055eb2e445263b89a
- https://git.kernel.org/stable/c/838fe9c28121777c59a9406710a68fcf77bb8017
- https://git.kernel.org/stable/c/d0a81ed5ff5d0f9c3f63a4f9e5a4642c363ecd3e
- https://git.kernel.org/stable/c/e1d1e203a6000804c5d3b8a4aa4e52303c0c7ab2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63809.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63809
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
