# [C] net/smc: protect link down work from execute after lgr freed

## Summary
Severity: Critical
Advisory: CVE-2024-56718
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56718
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.1.122, >=6.2.0 <6.6.68, >=6.7.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: protect link down work from execute after lgr freed

link down work may be scheduled before lgr freed but execute
after lgr freed, which may result in crash. So it is need to
hold a reference before shedule link down work, and put the
reference after work executed or canceled.

The relevant crash call stack as follows:
 list_del corruption. prev->next should be ffffb638c9c0fe20,
    but was 0000000000000000
 ------------[ cut here ]------------
 kernel BUG at lib/list_debug.c:51!
 invalid opcode: 0000 [#1] SMP NOPTI
 CPU: 6 PID: 978112 Comm: kworker/6:119 Kdump: loaded Tainted: G #1
 Hardware name: Alibaba Cloud Alibaba Cloud ECS, BIOS 2221b89 04/01/2014
 Workqueue: events smc_link_down_work [smc]
 RIP: 0010:__list_del_entry_valid.cold+0x31/0x47
 RSP: 0018:ffffb638c9c0fdd8 EFLAGS: 00010086
 RAX: 0000000000000054 RBX: ffff942fb75e5128 RCX: 0000000000000000
 RDX: ffff943520930aa0 RSI: ffff94352091fc80 RDI: ffff94352091fc80
 RBP: 0000000000000000 R08: 0000000000000000 R09: ffffb638c9c0fc38
 R10: ffffb638c9c0fc30 R11: ffffffffa015eb28 R12: 0000000000000002
 R13: ffffb638c9c0fe20 R14: 0000000000000001 R15: ffff942f9cd051c0
 FS:  0000000000000000(0000) GS:ffff943520900000(0000) knlGS:0000000000000000
 CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 00007f4f25214000 CR3: 000000025fbae004 CR4: 00000000007706e0
 DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
 DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
 PKRU: 55555554
 Call Trace:
  rwsem_down_write_slowpath+0x17e/0x470
  smc_link_down_work+0x3c/0x60 [smc]
  process_one_work+0x1ac/0x350
  worker_thread+0x49/0x2f0
  ? rescuer_thread+0x360/0x360
  kthread+0x118/0x140
  ? __kthread_bind_mask+0x60/0x60
  ret_from_fork+0x1f/0x30

## References
- https://git.kernel.org/stable/c/2627c3e8646932dfc7b9722c88c2e1ffcf7a9fb2
- https://git.kernel.org/stable/c/2b33eb8f1b3e8c2f87cfdbc8cc117f6bdfabc6ec
- https://git.kernel.org/stable/c/841b1824750d3b8d1dc0a96b14db4418b952abbc
- https://git.kernel.org/stable/c/bec2f52866d511e94c1c37cd962e4382b1b1a299
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56718.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
