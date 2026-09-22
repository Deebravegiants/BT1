# [M] scsi: lpfc: Fix SCSI I/O completion and abort handler deadlock

## Summary
Severity: Medium
Advisory: CVE-2022-49536
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49536
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Fix SCSI I/O completion and abort handler deadlock

During stress I/O tests with 500+ vports, hard LOCKUP call traces are
observed.

CPU A:
 native_queued_spin_lock_slowpath+0x192
 _raw_spin_lock_irqsave+0x32
 lpfc_handle_fcp_err+0x4c6
 lpfc_fcp_io_cmd_wqe_cmpl+0x964
 lpfc_sli4_fp_handle_cqe+0x266
 __lpfc_sli4_process_cq+0x105
 __lpfc_sli4_hba_process_cq+0x3c
 lpfc_cq_poll_hdler+0x16
 irq_poll_softirq+0x76
 __softirqentry_text_start+0xe4
 irq_exit+0xf7
 do_IRQ+0x7f

CPU B:
 native_queued_spin_lock_slowpath+0x5b
 _raw_spin_lock+0x1c
 lpfc_abort_handler+0x13e
 scmd_eh_abort_handler+0x85
 process_one_work+0x1a7
 worker_thread+0x30
 kthread+0x112
 ret_from_fork+0x1f

Diagram of lockup:

CPUA                            CPUB
----                            ----
lpfc_cmd->buf_lock
                            phba->hbalock
                            lpfc_cmd->buf_lock
phba->hbalock

Fix by reordering the taking of the lpfc_cmd->buf_lock and phba->hbalock in
lpfc_abort_handler routine so that it tries to take the lpfc_cmd->buf_lock
first before phba->hbalock.

## References
- https://git.kernel.org/stable/c/03cbbd7c2f5ee288f648f4aeedc765a181188553
- https://git.kernel.org/stable/c/0c4eed901285b9cae36a622f32bea3e92490da6c
- https://git.kernel.org/stable/c/21c0d469349957b5dc811c41200a2a998996ca8d
- https://git.kernel.org/stable/c/7625e81de2164a082810e1f27547d388406da610
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49536.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49536
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
