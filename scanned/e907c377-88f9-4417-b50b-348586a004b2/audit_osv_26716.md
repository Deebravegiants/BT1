# [H] bpf, cpumap: Handle skb as well when clean up ptr_ring

## Summary
Severity: High
Advisory: CVE-2023-53660
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53660
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.126, >=5.16.0 <6.1.45, >=6.2.0 <6.4.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, cpumap: Handle skb as well when clean up ptr_ring

The following warning was reported when running xdp_redirect_cpu with
both skb-mode and stress-mode enabled:

  ------------[ cut here ]------------
  Incorrect XDP memory type (-2128176192) usage
  WARNING: CPU: 7 PID: 1442 at net/core/xdp.c:405
  Modules linked in:
  CPU: 7 PID: 1442 Comm: kworker/7:0 Tainted: G  6.5.0-rc2+ #1
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996)
  Workqueue: events __cpu_map_entry_free
  RIP: 0010:__xdp_return+0x1e4/0x4a0
  ......
  Call Trace:
   <TASK>
   ? show_regs+0x65/0x70
   ? __warn+0xa5/0x240
   ? __xdp_return+0x1e4/0x4a0
   ......
   xdp_return_frame+0x4d/0x150
   __cpu_map_entry_free+0xf9/0x230
   process_one_work+0x6b0/0xb80
   worker_thread+0x96/0x720
   kthread+0x1a5/0x1f0
   ret_from_fork+0x3a/0x70
   ret_from_fork_asm+0x1b/0x30
   </TASK>

The reason for the warning is twofold. One is due to the kthread
cpu_map_kthread_run() is stopped prematurely. Another one is
__cpu_map_ring_cleanup() doesn't handle skb mode and treats skbs in
ptr_ring as XDP frames.

Prematurely-stopped kthread will be fixed by the preceding patch and
ptr_ring will be empty when __cpu_map_ring_cleanup() is called. But
as the comments in __cpu_map_ring_cleanup() said, handling and freeing
skbs in ptr_ring as well to "catch any broken behaviour gracefully".

## References
- https://git.kernel.org/stable/c/7c62b75cd1a792e14b037fa4f61f9b18914e7de1
- https://git.kernel.org/stable/c/937345720d18f1ad006ba3d5dcb3fa121037b8a2
- https://git.kernel.org/stable/c/b58d34068fd9f96bfc7d389988dfaf9a92a8fe00
- https://git.kernel.org/stable/c/cbd000451885801e9bbfd9cf7a7946806a85cb5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53660.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53660
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
