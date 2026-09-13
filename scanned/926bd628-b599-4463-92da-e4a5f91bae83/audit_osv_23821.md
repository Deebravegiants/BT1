# [M] scsi: lpfc: Protect memory leak for NPIV ports sending PLOGI_RJT

## Summary
Severity: Medium
Advisory: CVE-2022-49534
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49534
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: lpfc: Protect memory leak for NPIV ports sending PLOGI_RJT

There is a potential memory leak in lpfc_ignore_els_cmpl() and
lpfc_els_rsp_reject() that was allocated from NPIV PLOGI_RJT
(lpfc_rcv_plogi()'s login_mbox).

Check if cmdiocb->context_un.mbox was allocated in lpfc_ignore_els_cmpl(),
and then free it back to phba->mbox_mem_pool along with mbox->ctx_buf for
service parameters.

For lpfc_els_rsp_reject() failure, free both the ctx_buf for service
parameters and the login_mbox.

## References
- https://git.kernel.org/stable/c/672d1cb40551ea9c95efad43ab6d45e4ab4e015f
- https://git.kernel.org/stable/c/c00df0f34a6d5e14da379f96ea67e501ce67b002
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49534.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49534
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
