# [H] net/smc: use smc_lgr_list.lock to protect smc_lgr_list.list iterate in smcr_port_add

## Summary
Severity: High
Advisory: CVE-2023-54318
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54318
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.54, >=6.2.0 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: use smc_lgr_list.lock to protect smc_lgr_list.list iterate in smcr_port_add

While doing smcr_port_add, there maybe linkgroup add into or delete
from smc_lgr_list.list at the same time, which may result kernel crash.
So, use smc_lgr_list.lock to protect smc_lgr_list.list iterate in
smcr_port_add.

The crash calltrace show below:
BUG: kernel NULL pointer dereference, address: 0000000000000000
PGD 0 P4D 0
Oops: 0000 [#1] SMP NOPTI
CPU: 0 PID: 559726 Comm: kworker/0:92 Kdump: loaded Tainted: G
Hardware name: Alibaba Cloud Alibaba Cloud ECS, BIOS 449e491 04/01/2014
Workqueue: events smc_ib_port_event_work [smc]
RIP: 0010:smcr_port_add+0xa6/0xf0 [smc]
RSP: 0000:ffffa5a2c8f67de0 EFLAGS: 00010297
RAX: 0000000000000001 RBX: ffff9935e0650000 RCX: 0000000000000000
RDX: 0000000000000010 RSI: ffff9935e0654290 RDI: ffff9935c8560000
RBP: 0000000000000000 R08: 0000000000000000 R09: ffff9934c0401918
R10: 0000000000000000 R11: ffffffffb4a5c278 R12: ffff99364029aae4
R13: ffff99364029aa00 R14: 00000000ffffffed R15: ffff99364029ab08
FS:  0000000000000000(0000) GS:ffff994380600000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000000000000000 CR3: 0000000f06a10003 CR4: 0000000002770ef0
PKRU: 55555554
Call Trace:
 smc_ib_port_event_work+0x18f/0x380 [smc]
 process_one_work+0x19b/0x340
 worker_thread+0x30/0x370
 ? process_one_work+0x340/0x340
 kthread+0x114/0x130
 ? __kthread_cancel_work+0x50/0x50
 ret_from_fork+0x1f/0x30

## References
- https://git.kernel.org/stable/c/06b4934ab2b534bb92935c7601852066ebb9eab8
- https://git.kernel.org/stable/c/70c8d17007dc4a07156b7da44509527990e569b3
- https://git.kernel.org/stable/c/b717463610a27fc0b58484cfead7a623d5913e61
- https://git.kernel.org/stable/c/d1c6c93c27a4bf48006ab16cd9b38d85559d7645
- https://git.kernel.org/stable/c/f5146e3ef0a9eea405874b36178c19a4863b8989
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54318.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
