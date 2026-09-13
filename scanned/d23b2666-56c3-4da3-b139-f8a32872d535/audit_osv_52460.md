# [M] CVE-2021-47473

## Summary
Severity: Medium
Advisory: CVE-2021-47473
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47473
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix a memory leak in an error path of qla2x00_process_els()

Commit 8c0eb596baa5 ("[SCSI] qla2xxx: Fix a memory leak in an error path of
qla2x00_process_els()"), intended to change:

        bsg_job->request->msgcode == FC_BSG_HST_ELS_NOLOGIN


        bsg_job->request->msgcode != FC_BSG_RPT_ELS

but changed it to:

        bsg_job->request->msgcode == FC_BSG_RPT_ELS

instead.

Change the == to a != to avoid leaking the fcport structure or freeing
unallocated memory.

## References
- https://git.kernel.org/stable/c/7fb223d0ad801f633c78cbe42b1d1b55f5d163ad
- https://git.kernel.org/stable/c/96f0aebf29be25254fa585af43924e34aa21fd9a
- https://git.kernel.org/stable/c/a7fbb56e6c941d9f59437b96412a348e66388d3e
