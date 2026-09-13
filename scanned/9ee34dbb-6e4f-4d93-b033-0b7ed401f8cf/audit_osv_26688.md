# [H] bpf, cpumap: Make sure kthread is running before map update returns

## Summary
Severity: High
Advisory: CVE-2023-53577
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-04
Source: https://osv.dev/vulnerability/CVE-2023-53577
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.15.126, >=5.16.0 <6.1.45, >=6.2.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, cpumap: Make sure kthread is running before map update returns

The following warning was reported when running stress-mode enabled
xdp_redirect_cpu with some RT threads:

  ------------[ cut here ]------------
  WARNING: CPU: 4 PID: 65 at kernel/bpf/cpumap.c:135
  CPU: 4 PID: 65 Comm: kworker/4:1 Not tainted 6.5.0-rc2+ #1
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
  Workqueue: events cpu_map_kthread_stop
  RIP: 0010:put_cpu_map_entry+0xda/0x220
  ......
  Call Trace:
   <TASK>
   ? show_regs+0x65/0x70
   ? __warn+0xa5/0x240
   ......
   ? put_cpu_map_entry+0xda/0x220
   cpu_map_kthread_stop+0x41/0x60
   process_one_work+0x6b0/0xb80
   worker_thread+0x96/0x720
   kthread+0x1a5/0x1f0
   ret_from_fork+0x3a/0x70
   ret_from_fork_asm+0x1b/0x30
   </TASK>

The root cause is the same as commit 436901649731 ("bpf: cpumap: Fix memory
leak in cpu_map_update_elem"). The kthread is stopped prematurely by
kthread_stop() in cpu_map_kthread_stop(), and kthread() doesn't call
cpu_map_kthread_run() at all but XDP program has already queued some
frames or skbs into ptr_ring. So when __cpu_map_ring_cleanup() checks
the ptr_ring, it will find it was not emptied and report a warning.

An alternative fix is to use __cpu_map_ring_cleanup() to drop these
pending frames or skbs when kthread_stop() returns -EINTR, but it may
confuse the user, because these frames or skbs have been handled
correctly by XDP program. So instead of dropping these frames or skbs,
just make sure the per-cpu kthread is running before
__cpu_map_entry_alloc() returns.

After apply the fix, the error handle for kthread_stop() will be
unnecessary because it will always return 0, so just remove it.

## References
- https://git.kernel.org/stable/c/640a604585aa30f93e39b17d4d6ba69fcb1e66c9
- https://git.kernel.org/stable/c/7a1178a3671b40746830d355836b72e47ceb2490
- https://git.kernel.org/stable/c/b44d28b98f185d2f2348aa3c3636838c316f889e
- https://git.kernel.org/stable/c/ecb45b852af5e88257020b88bea5ff0798d72aca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53577.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53577
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
