# [H] scsi: qla2xxx: Validate sp before freeing associated memory

## Summary
Severity: High
Advisory: CVE-2025-71236
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2025-71236
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.251, >=5.11.0 <5.15.201, >=5.16.0 <6.1.164, >=6.2.0 <6.6.125, >=6.7.0 <6.12.72, >=6.13.0 <6.18.11, >=6.19.0 <6.19.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Validate sp before freeing associated memory

System crash with the following signature
[154563.214890] nvme nvme2: NVME-FC{1}: controller connect complete
[154564.169363] qla2xxx [0000:b0:00.1]-3002:2: nvme: Sched: Set ZIO exchange threshold to 3.
[154564.169405] qla2xxx [0000:b0:00.1]-ffffff:2: SET ZIO Activity exchange threshold to 5.
[154565.539974] qla2xxx [0000:b0:00.1]-5013:2: RSCN database changed – 0078 0080 0000.
[154565.545744] qla2xxx [0000:b0:00.1]-5013:2: RSCN database changed – 0078 00a0 0000.
[154565.545857] qla2xxx [0000:b0:00.1]-11a2:2: FEC=enabled (data rate).
[154565.552760] qla2xxx [0000:b0:00.1]-11a2:2: FEC=enabled (data rate).
[154565.553079] BUG: kernel NULL pointer dereference, address: 00000000000000f8
[154565.553080] #PF: supervisor read access in kernel mode
[154565.553082] #PF: error_code(0x0000) - not-present page
[154565.553084] PGD 80000010488ab067 P4D 80000010488ab067 PUD 104978a067 PMD 0
[154565.553089] Oops: 0000 1 PREEMPT SMP PTI
[154565.553092] CPU: 10 PID: 858 Comm: qla2xxx_2_dpc Kdump: loaded Tainted: G           OE     -------  ---  5.14.0-503.11.1.el9_5.x86_64 #1
[154565.553096] Hardware name: HPE Synergy 660 Gen10/Synergy 660 Gen10 Compute Module, BIOS I43 09/30/2024
[154565.553097] RIP: 0010:qla_fab_async_scan.part.0+0x40b/0x870 [qla2xxx]
[154565.553141] Code: 00 00 e8 58 a3 ec d4 49 89 e9 ba 12 20 00 00 4c 89 e6 49 c7 c0 00 ee a8 c0 48 c7 c1 66 c0 a9 c0 bf 00 80 00 10 e8 15 69 00 00 <4c> 8b 8d f8 00 00 00 4d 85 c9 74 35 49 8b 84 24 00 19 00 00 48 8b
[154565.553143] RSP: 0018:ffffb4dbc8aebdd0 EFLAGS: 00010286
[154565.553145] RAX: 0000000000000000 RBX: ffff8ec2cf0908d0 RCX: 0000000000000002
[154565.553147] RDX: 0000000000000000 RSI: ffffffffc0a9c896 RDI: ffffb4dbc8aebd47
[154565.553148] RBP: 0000000000000000 R08: ffffb4dbc8aebd45 R09: 0000000000ffff0a
[154565.553150] R10: 0000000000000000 R11: 000000000000000f R12: ffff8ec2cf0908d0
[154565.553151] R13: ffff8ec2cf090900 R14: 0000000000000102 R15: ffff8ec2cf084000
[154565.553152] FS:  0000000000000000(0000) GS:ffff8ed27f800000(0000) knlGS:0000000000000000
[154565.553154] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[154565.553155] CR2: 00000000000000f8 CR3: 000000113ae0a005 CR4: 00000000007706f0
[154565.553157] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
[154565.553158] DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
[154565.553159] PKRU: 55555554
[154565.553160] Call Trace:
[154565.553162]  <TASK>
[154565.553165]  ? show_trace_log_lvl+0x1c4/0x2df
[154565.553172]  ? show_trace_log_lvl+0x1c4/0x2df
[154565.553177]  ? qla_fab_async_scan.part.0+0x40b/0x870 [qla2xxx]
[154565.553215]  ? __die_body.cold+0x8/0xd
[154565.553218]  ? page_fault_oops+0x134/0x170
[154565.553223]  ? snprintf+0x49/0x70
[154565.553229]  ? exc_page_fault+0x62/0x150
[154565.553238]  ? asm_exc_page_fault+0x22/0x30

Check for sp being non NULL before freeing any associated memory

## References
- https://git.kernel.org/stable/c/044131fce27749cb6ea986baf861fbe63c6d8a17
- https://git.kernel.org/stable/c/1a9585e4c58d1f1662b3ca46110ed4f583082ce5
- https://git.kernel.org/stable/c/40ae93668226b610edb952c6036f607a61750b57
- https://git.kernel.org/stable/c/85c0890fea6baeba9c4ae6ae090182cbb1a93fb2
- https://git.kernel.org/stable/c/944378ead9a48d5d50e9e3cc85e4cdb911c37ca1
- https://git.kernel.org/stable/c/949010291bb941d53733ed08a33454254d9afb1b
- https://git.kernel.org/stable/c/a46f81c1e627437de436e517f5fd4b725c15a1e6
- https://git.kernel.org/stable/c/b6df15aec8c3441357d4da0eaf4339eb20f5999f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71236.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
