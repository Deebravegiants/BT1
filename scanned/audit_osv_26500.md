# [M] scsi: qla2xxx: Remove unused nvme_ls_waitq wait queue

## Summary
Severity: Medium
Advisory: CVE-2023-53280
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53280
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Remove unused nvme_ls_waitq wait queue

System crash when qla2x00_start_sp(sp) returns error code EGAIN and wake_up
gets called for uninitialized wait queue sp->nvme_ls_waitq.

    qla2xxx [0000:37:00.1]-2121:5: Returning existing qpair of ffff8ae2c0513400 for idx=0
    qla2xxx [0000:37:00.1]-700e:5: qla2x00_start_sp failed = 11
    BUG: unable to handle kernel NULL pointer dereference at 0000000000000000
    PGD 0 P4D 0
    Oops: 0000 [#1] SMP NOPTI
    Hardware name: HPE ProLiant DL360 Gen10/ProLiant DL360 Gen10, BIOS U32 09/03/2021
    Workqueue: nvme-wq nvme_fc_connect_ctrl_work [nvme_fc]
    RIP: 0010:__wake_up_common+0x4c/0x190
    RSP: 0018:ffff95f3e0cb7cd0 EFLAGS: 00010086
    RAX: 0000000000000000 RBX: ffff8b08d3b26328 RCX: 0000000000000000
    RDX: 0000000000000001 RSI: 0000000000000003 RDI: ffff8b08d3b26320
    RBP: 0000000000000001 R08: 0000000000000000 R09: ffffffffffffffe8
    R10: 0000000000000000 R11: ffff95f3e0cb7a60 R12: ffff95f3e0cb7d20
    R13: 0000000000000003 R14: 0000000000000000 R15: 0000000000000000
    FS:  0000000000000000(0000) GS:ffff8b2fdf6c0000(0000) knlGS:0000000000000000
    CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
    CR2: 0000000000000000 CR3: 0000002f1e410002 CR4: 00000000007706e0
    DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
    DR3: 0000000000000000 DR6: 00000000fffe0ff0 DR7: 0000000000000400
    PKRU: 55555554
    Call Trace:
     __wake_up_common_lock+0x7c/0xc0
     qla_nvme_ls_req+0x355/0x4c0 [qla2xxx]
     ? __nvme_fc_send_ls_req+0x260/0x380 [nvme_fc]
     ? nvme_fc_send_ls_req.constprop.42+0x1a/0x45 [nvme_fc]
     ? nvme_fc_connect_ctrl_work.cold.63+0x1e3/0xa7d [nvme_fc]

Remove unused nvme_ls_waitq wait queue. nvme_ls_waitq logic was removed
previously in the commits tagged Fixed: below.

## References
- https://git.kernel.org/stable/c/0b1ce92fabdb7d02ddf8641230a06e2752ae5baa
- https://git.kernel.org/stable/c/20fce500b232b970e40312a9c97e7f3b6d7a709c
- https://git.kernel.org/stable/c/522ee1b3030f3b6b5fd59489d12b4ca767c9e5da
- https://git.kernel.org/stable/c/92529387a0066754fd9cda080fb3298b8cca750c
- https://git.kernel.org/stable/c/b7084ebf4f54d46fed5153112d685f4137334175
- https://git.kernel.org/stable/c/f459d586fdf12c53116c9fddf43065165fdd5969
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53280.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53280
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
