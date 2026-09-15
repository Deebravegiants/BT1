# [H] scsi: qla2xxx: Complete command early within lock

## Summary
Severity: High
Advisory: CVE-2024-42287
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42287
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.103, >=6.2.0 <6.6.44, >=6.3.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Complete command early within lock

A crash was observed while performing NPIV and FW reset,

 BUG: kernel NULL pointer dereference, address: 000000000000001c
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: 0000 1 PREEMPT_RT SMP NOPTI
 RIP: 0010:dma_direct_unmap_sg+0x51/0x1e0
 RSP: 0018:ffffc90026f47b88 EFLAGS: 00010246
 RAX: 0000000000000000 RBX: 0000000000000021 RCX: 0000000000000002
 RDX: 0000000000000021 RSI: 0000000000000000 RDI: ffff8881041130d0
 RBP: ffff8881041130d0 R08: 0000000000000000 R09: 0000000000000034
 R10: ffffc90026f47c48 R11: 0000000000000031 R12: 0000000000000000
 R13: 0000000000000000 R14: ffff8881565e4a20 R15: 0000000000000000
 FS: 00007f4c69ed3d00(0000) GS:ffff889faac80000(0000) knlGS:0000000000000000
 CS: 0010 DS: 0000 ES: 0000 CR0: 0000000080050033
 CR2: 000000000000001c CR3: 0000000288a50002 CR4: 00000000007706e0
 DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
 DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
 PKRU: 55555554
 Call Trace:
 <TASK>
 ? __die_body+0x1a/0x60
 ? page_fault_oops+0x16f/0x4a0
 ? do_user_addr_fault+0x174/0x7f0
 ? exc_page_fault+0x69/0x1a0
 ? asm_exc_page_fault+0x22/0x30
 ? dma_direct_unmap_sg+0x51/0x1e0
 ? preempt_count_sub+0x96/0xe0
 qla2xxx_qpair_sp_free_dma+0x29f/0x3b0 [qla2xxx]
 qla2xxx_qpair_sp_compl+0x60/0x80 [qla2xxx]
 __qla2x00_abort_all_cmds+0xa2/0x450 [qla2xxx]

The command completion was done early while aborting the commands in driver
unload path but outside lock to avoid the WARN_ON condition of performing
dma_free_attr within the lock. However this caused race condition while
command completion via multiple paths causing system crash.

Hence complete the command early in unload path but within the lock to
avoid race condition.

## References
- https://git.kernel.org/stable/c/314efe3f87949a568f512f05df20bf47b81cf232
- https://git.kernel.org/stable/c/36fdc5319c4d0ec8b8938ec4769764098a246bfb
- https://git.kernel.org/stable/c/4475afa2646d3fec176fc4d011d3879b26cb26e3
- https://git.kernel.org/stable/c/57ba7563712227647f82a92547e82c96cd350553
- https://git.kernel.org/stable/c/814f4a53cc86f7ea8b501bfb1723f24fd29ef5ee
- https://git.kernel.org/stable/c/9117337b04d789bd08fdd9854a40bec2815cd3f6
- https://git.kernel.org/stable/c/af46649304b0c9cede4ccfc2be2561ce8ed6a2ea
- https://lists.debian.org/debian-lts-announce/2024/10/msg00003.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42287.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
